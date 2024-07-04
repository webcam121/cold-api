from django.conf import settings
from google.ads.googleads.client import GoogleAdsClient
from datetime import datetime, timezone

CUSTOMER_ID = '7230121642'


# def run():
#     from google.ads.googleads.client import GoogleAdsClient
#
#     # Initialize the Google Ads client
#     client = GoogleAdsClient.load_from_env()
#
#     # Get the service
#     service = client.get_service("GoogleAdsService")
#
#     # Set your customer ID
#     customer_id = "1006381692"
#
#     # Create the query
#     query = """
#         SELECT conversion_action.id, conversion_action.name
#         FROM conversion_action
#     """
#
#     # Execute the query
#     response = service.search_stream(customer_id=customer_id, query=query)
#
#     # Process the response
#     for batch in response:
#         for row in batch.results:
#             print(f"Conversion Action ID: {row.conversion_action.id} - Name: {row.conversion_action.name}")

def upload_conversion(
    gclid,
    conversion_value,
    conversion_action_id,
    conversion_custom_variable_id=None,
    conversion_custom_variable_value=None,
    gbraid=None,
    wbraid=None,
):
    if settings.ENVIRONMENT != 'production':
        return
    try:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z')
        conversion_date_time = f"{now[:-4]}{now[-4:-2]}:{now[-2:]}"
        """Creates a click conversion with a default currency of USD.
        Args:
            client: An initialized GoogleAdsClient instance.
            customer_id: The client customer ID string.
            conversion_action_id: The ID of the conversion action to upload to.
            gclid: The Google Click Identifier ID. If set, the wbraid and gbraid
                parameters must be None.
            conversion_date_time: The the date and time of the conversion (should be
                after the click time). The format is 'yyyy-mm-dd hh:mm:ss+|-hh:mm',
                e.g. '2021-01-01 12:32:45-08:00'.
            conversion_value: The conversion value in the desired currency.
            conversion_custom_variable_id: The ID of the conversion custom
                variable to associate with the upload.
            conversion_custom_variable_value: The str value of the conversion custom
                variable to associate with the upload.
            gbraid: The GBRAID for the iOS app conversion. If set, the gclid and
                wbraid parameters must be None.
            wbraid: The WBRAID for the iOS app conversion. If set, the gclid and
                gbraid parameters must be None.
        """
        client = GoogleAdsClient.load_from_env()

        click_conversion = client.get_type("ClickConversion")
        conversion_action_service = client.get_service("ConversionActionService")
        click_conversion.conversion_action = conversion_action_service.conversion_action_path(
            CUSTOMER_ID, conversion_action_id
        )
        # Sets the single specified ID field.
        if gclid:
            click_conversion.gclid = gclid
        elif gbraid:
            click_conversion.gbraid = gbraid
        elif wbraid:
            click_conversion.wbraid = wbraid
        else:
            return

        click_conversion.conversion_date_time = conversion_date_time
        if conversion_value:
            click_conversion.conversion_value = float(conversion_value)
            click_conversion.currency_code = "USD"

        if conversion_custom_variable_id and conversion_custom_variable_value:
            conversion_custom_variable = client.get_type("CustomVariable")
            conversion_custom_variable.conversion_custom_variable = conversion_custom_variable_id
            conversion_custom_variable.value = conversion_custom_variable_value
            click_conversion.custom_variables.append(conversion_custom_variable)

        conversion_upload_service = client.get_service("ConversionUploadService")
        request = client.get_type("UploadClickConversionsRequest")
        request.customer_id = CUSTOMER_ID
        request.conversions.append(click_conversion)
        request.partial_failure = True
        conversion_upload_response = conversion_upload_service.upload_click_conversions(
            request=request,
        )
        return str(conversion_upload_response)
    except Exception as e:
        print("ERROR", e)
        raise ValueError('ERROR GOOGLE')