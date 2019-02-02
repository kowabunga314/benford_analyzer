import re
import io
from math import floor, log10
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from ingestor.models import BenfordRequest
from .models import Ingestor
from .serializers import BenfordRequestSerializer, IngestorSerializer
from .config import BENFORD_DISTRIBUTION as BD, BENFORD_TOLERANCE as BT


class Benford(APIView):

    # Only allow this view for POST methods
    @require_http_methods(['POST'])
    # Disable CSRF token because we're not authenticating users
    @method_decorator(csrf_exempt)
    def analyze(self):
        # Clear database for clean run
        Ingestor.objects.all().delete()

        # Serialize and validate input data
        data = {'column': self.POST['column'], 'separator': self.POST['separator'], 'file': self.FILES['file']}
        b_ser = BenfordRequestSerializer(data=data)

        if b_ser.is_valid():
            br = b_ser.save()
        else:
            return JsonResponse({'message': 'Failed to parse file data. Please verify correct column and separator '
                                            'values'}, status=400)

        # Parse retrieved values
        try:
            Benford.import_values(br)
        except ValidationError:
            return JsonResponse({'message': 'Failed to parse file data. Please verify correct column and separator '
                                            'values'}, status=400)
        except Exception as e:
            # Using broad exception class here for debugging. More specific exception handling can be
            # implemented after testing
            return JsonResponse({'message': e.__str__()}, status=400)

        # Analyze imported values
        try:
            response = Benford.generate_response(br)
        except Exception as e:
            # Using broad exception class here for debugging. More specific exception handling can be
            # implemented after testing
            return JsonResponse({'message': e.__str__()}, status=500)

        return JsonResponse(response)

    @staticmethod
    def import_values(br):
        # Get file data from memory
        file = io.StringIO(br.file.read().decode())
        # Iterate through file
        for i, line in enumerate(file):
            # Skip header row
            if i == 0:
                continue

            # Grab the value from specified column
            try:
                lst = line.split(br.get_separator_display())
                col = lst[br.column]
                value = col.strip()
            except IndexError:
                # Failed to extract numerical data, try with regex as a backup.
                # This method is risky and may not provide the most accurate data.
                reg = r'\d+'
                try:
                    value = re.search(reg, line).group(0)
                except AttributeError:
                    # We are unable to retrieve a numerical value from this row. Move on to next iteration of loop.
                    continue
            i_ser = IngestorSerializer(data={'value': value})

            # Validate data prior to saving to DB
            if i_ser.is_valid():
                # Data was valid, saving to DB
                i_ser.save()
            else:
                # Data was invalid, possibly indicating we're not looking at the correct column
                raise ValidationError('ailed to parse file data. Please verify correct column and separator values')

    @staticmethod
    def generate_response(br):
        i = Ingestor.objects.all()
        digits = []

        # Generate analysis for each digit
        for num in range(1, 10):
            digits.append({
                'digit': num,
                'count': i.filter(msd=num).count(),
                # (occurrences/total*100)
                'percent': round(i.filter(msd=num).count()/i.count()*100, 2)
            })

        # Generate full response with benford match and file name
        response_data = {
            'first_digit_distribution': digits,
            # (30% - tolerance) < distribution of 1 as leading digit < (30% + tolerance)
            'benford_match': (BD - BT) < round(i.filter(msd=1).count()/i.count()*100, 2) < (BD + BT),
            'file': br.file.name
        }

        return response_data
