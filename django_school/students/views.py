from datetime import datetime
import json

from django.conf import settings
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth import get_user_model

from schools.mixins import StudentRequiredMixin
from schools.models import Event
from classroom.models import ClassRoom
from classroom.views.timetable import get_timetable_periods
from teachers.decorators import teacher_required

from .decorators import student_required
from .forms import StudentSignUpForm
from .models import Student

class StudentSignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = StudentSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['usertype'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')#students:quiz_list')


@method_decorator([login_required, student_required], name='dispatch')
class EventList(View):
    def get(self, request):
        flag = request.GET.get('json','')
        if flag: 
            events= Event.objects.filter(school = request.user.school)
            qs_json = [dict(id=et.id, title=et.title, start=str(et.startdatetime)) for et in events]
            return JsonResponse(qs_json,safe=False)

        return render(request,'students/events.html')

@method_decorator([login_required,student_required], name='dispatch')
class TimeTableView(View):
    def get(self, request):
        qs_json = get_timetable_periods(request.user.student.classroom)
        return JsonResponse(qs_json,safe=False)

@method_decorator([login_required, teacher_required], name='dispatch')
class UserList(View):
    def get(self, request, usertype="1"):
        # if not usertype: usertype = 1
        queryset = get_user_model().objects.filter(school = request.user.school, user_type = usertype)
        return render(request,'students/user_list.html',{'users':queryset,'page': usertype})

    def post(self,request, usertype="1"):
        user_id = request.POST.get('user','')
        verified = request.POST.get('verified', '')
        if user_id:
            user = get_user_model().objects.get(id = user_id)
            if verified == 'on': 
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()

        if usertype=="1":
            return redirect('students:user_list')
        return redirect('students:user_list', usertype)

@method_decorator([login_required, teacher_required], name='dispatch')
class StudentImport(View):
    def get(self, request):
        classrooms = ClassRoom.objects.filter(school = request.user.school)
        return render(request,'students/student_import.html',{'classrooms':classrooms })

    def post(self,request):
        import json
        classroom = request.POST['classroom']
        if not classroom:
            return HttpResponse('Please select a ClassRoom.')
        User = get_user_model()
        users = []
        for row in json.loads(request.POST['data']):
            if any(row):

                fname,lname,email,dob = row
                # if fname and lname and dob and email:
                if all(row):
                    if User.objects.filter(username=email):
                        return HttpResponse('Email:{} already exists. Please provide different email.'.format(email))
                    user = User(
                        first_name=fname,
                        last_name=lname,
                        is_staff=True,
                        username=email,
                        user_type=1,
                        school=request.user.school
                    )
                    user.set_password(dob)
                    users.append(user)
                    # user = get_user_model().objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
                else:
                    return HttpResponse('All fields are required.')

        for user in users:
            user.save()
            student = Student.objects.create(user=user,classroom_id = classroom)

        # User.objects.bulk_create(users)            
        return HttpResponse('success')




from django.http import JsonResponse
from datetime import date, datetime,timedelta
from classroom.models import Attendance

class AttendanceView(StudentRequiredMixin, View):

    def get(self, request):
        middle  = timedelta(days=15)
        start = datetime.fromtimestamp(int(request.GET['start'])) + middle
        attendances = Attendance.objects.filter(
            student__user=request.user, 
            attendanceclass__date__year = start.year,
            attendanceclass__date__month = start.month,
        )
        # print(attendances)
        resp = {}
        for attendance in attendances:
            item = int(attendance.attendanceclass.date.strftime("%s%f"))/1000000
            status = 2 if attendance.status == 'P' else 3
            resp[str(item)]=status
        # present = int(date(2019,1,15).strftime("%s%f"))/1000000
        
        return JsonResponse(resp,safe=False)