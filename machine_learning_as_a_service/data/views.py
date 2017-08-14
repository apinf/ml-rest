import pandas as pd
import requests

from django.shortcuts import render

from data.models import Data

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
            data = Data()

            # Add CSV Data to data_frame field
            data.data_frame = csv_data

            # Save Data Frame
            data.save()
