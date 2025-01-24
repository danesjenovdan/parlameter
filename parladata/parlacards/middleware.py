from datetime import datetime

from django.http import JsonResponse


class ParlacardsMiddleware:
    """
    Checks the presence and correctness of id and date,
    parameter returns 400 if something is wrong, otherwise
    casts and assigns them to the request object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # only trigger if it's a /cards/ url
        if "/cards/" not in request.path:
            return self.get_response(request)

        if request.method == "POST":
            # if request method is POST we don't need card_date and card_id
            return self.get_response(request)

        # get params
        request_id = request.GET.get("id", None)
        date_string = request.GET.get("date", datetime.now().strftime("%Y-%m-%d"))

        # if no id was supplied, return
        if not request_id:
            content = {"error": "`id` is required."}
            return JsonResponse(content, status=400)
            # we return a JsonResponse instead of DRF's Response
            # return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # if id is not an integer return
        try:
            request.card_id = int(request_id)
        except ValueError:
            content = {"error": "`id` needs to be an integer."}
            return JsonResponse(content, status=400)

        # try parsing the date
        try:
            parsed_datetime = datetime.strptime(date_string, "%Y-%m-%d")
            # by default parsed_datetime will be at 00:00:00 (start of day)
            # to properly compare the date with `<=` and `__lte` set the time at
            # the end of the day so that timestamps on current day are included
            end_of_day_datetime = parsed_datetime.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            request.card_date = end_of_day_datetime
        # if the date could not be parsed, return
        except ValueError as e:
            content = {
                "error": f'Can not parse date. Please use the following format: {datetime.now().strftime("%Y-%m-%d")}'
            }
            return JsonResponse(content, status=400)
            # we return a JsonResponse instead of DRF's Response
            # return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return self.get_response(request)
