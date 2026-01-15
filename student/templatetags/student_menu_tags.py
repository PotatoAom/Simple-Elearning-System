from django import template
from home import models as hmodel

register = template.Library()

@register.inclusion_tag('student/student_menu.html', takes_context=True)
def student_menu(context, course):
    request = context.get('request')
    user = getattr(request, 'user', None)
    
    completed_class_ids = set()
    completed_assign_ids = set()
    
    classview = hmodel.Classroom.objects.filter(course_id=course).order_by('id')
    assignview = hmodel.Assignment.objects.filter(course_id=course).order_by('id')

    if user and user.is_authenticated:
        completed_class_ids = set(hmodel.ClassroomDone.objects.filter(classroom__course=course, user=user).values_list('classroom_id', flat=True))
        completed_assign_ids = set(hmodel.AssignmentFile.objects.filter(course=course, user=user).values_list('assign_id', flat=True))

    total_classrooms = classview.count()
    classroom_done = total_classrooms > 0 and (total_classrooms == len(completed_class_ids))

    total_assignments = assignview.count()
    assign_done = total_assignments > 0 and (total_assignments == len(completed_assign_ids))

    return {
        'course': course,
        'classview': classview,
        'assignview': assignview,
        'completed_class_ids': completed_class_ids,
        'completed_assign_ids': completed_assign_ids,
        'classroom_done': classroom_done,
        'assign': assign_done,
    }