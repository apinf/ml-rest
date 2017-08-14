import pandas as pd
import requests

from django.shortcuts import render

from data.models import DataFrame

# Create your views here.
def save_csv_as_dataframe(request):
    print("Save CSV as DataFrame")

    if (request.POST):
        # Get CSV URL from post; default to None if not provided
        csv_url = request.POST.get('csv_url', None)

        if (csv_url):
            csv_data = pd.read_csv(csv_url)

            print(csv_data)

            # Create Data Frame instance
            data_frame = DataFrame()

            # Add CSV Data to data_frame field
            data_frame.data_frame = csv_data

            # Save Data Frame
            data_frame.save()
