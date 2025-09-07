from rest_framework.decorators import api_view
from rest_framework.response import Response

from .reports import ReportsService


@api_view(['GET'])
def event_popularity(request):
    college_id = request.query_params.get('college')
    event_type = request.query_params.get('type')
    data = ReportsService.event_popularity(college_id, event_type)
    return Response(data)


@api_view(['GET'])
def student_participation(request, student_id: int):
    return Response(ReportsService.student_participation(student_id))


@api_view(['GET'])
def top_students(request):
    limit = int(request.query_params.get('limit', 3))
    college_id = request.query_params.get('college')
    return Response(ReportsService.top_students(limit=limit, college_id=college_id))
