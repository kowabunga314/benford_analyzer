from math import floor, log10
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import ValidationError

from .models import Ingestor
from .serializers import IngestorSerializer


@require_http_methods(['POST'])
def analyze(request):
    # Validate column and separator characters
    print('wumbo')

    # Parse file
    try:
        import_values(request.data.column, request.data.separator, request.data.file)
    except ValidationError:
        return JsonResponse({'message': 'Failed to parse file data. Please verify correct column and separator '
                                        'values'}, status=400)

    # Analyze imported values
    analyze_values(Ingestor.objects.all())


def import_values(column, separator, file):
    # Open file for reading
    with open(file, 'r') as file:
        # Skip header row
        next(file)
        # Read file into DB line-by-line
        for line in file:
            # Grab the value from specified column
            value = line.split(separator)[column].strip()
            i_ser = IngestorSerializer(data={'value': value})

            # Validate data prior to saving to DB
            if i_ser.is_valid():
                # Data was valid, saving to DB
                i_ser.save()
            else:
                # Data was invalid, possibly indicating we're not looking at the correct column
                raise ValidationError('ailed to parse file data. Please verify correct column and separator values')


def analyze_values(values):
    data = dict()

    for v in values:
        # Get most significant digit
        leading_digit = get_msd(v)
        if leading_digit in data:       # We already have a value for this key
            data[leading_digit] += 1
        else:                           # No value exists for this key
            data[leading_digit] = 1

    return get_formatted_response(data)


def get_formatted_response(data):
    total = Ingestor.objects.all().count()
    # Set basic format for return
    return_value = {
        'digit_distribution': []
    }

    # Iterate through keys in given dict
    for key in data:
        return_value['digit_distribution'].append({
            'digit': key,
            'count': data[key],
            'percent': round(data[key]/total*100, 2)
        })

    return return_value


def get_msd(num):
    return num // (10**floor(log10(num)))
