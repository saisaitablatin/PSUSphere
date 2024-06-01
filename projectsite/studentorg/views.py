import random
import json
from datetime import datetime
from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from studentorg.models import (
    Organization,
    OrgMember,
    Student,
    College,
    Program,
    FireIncident,
    FireLocation,
    FireStation,
)
from studentorg.forms import (
    OrganizationForm,
    OrgMemberForm,
    StudentForm,
    CollegeForm,
    ProgramForm,
)
from django.urls import reverse_lazy
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime


@method_decorator(login_required, name="dispatch")
class HomePageView(ListView):
    model = Organization
    context_object_name = "home"
    template_name = "chart.html"


class ChartView(ListView):
    template_name = "chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass


class OrganizationList(ListView):
    model = Organization
    context_object_name = "organization"
    template_name = "org_list.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrganizationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return qs


class OrganizationCreateView(CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "org_add.html"
    success_url = reverse_lazy("organization-list")


class OrganizationUpdateView(UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "org_edit.html"
    success_url = reverse_lazy("organization-list")


class OrganizationDeleteView(DeleteView):
    model = Organization
    template_name = "org_del.html"
    success_url = reverse_lazy("organization-list")


class OrgMemberList(ListView):
    model = OrgMember
    context_object_name = "orgmember"
    template_name = "orgmem_list.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(OrgMemberList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(
                Q(student__lastname__icontains=query)
                | Q(student__firstname__icontains=query)
                | Q(student__middlename__icontains=query)
                | Q(organization__name__icontains=query)
                | Q(date_joined__icontains=query)
            )
        return qs


class OrgMemberCreateView(CreateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = "orgmem_add.html"
    success_url = reverse_lazy("orgmember-list")


class OrgMemberUpdateView(UpdateView):
    model = OrgMember
    form_class = OrgMemberForm
    template_name = "orgmem_edit.html"
    success_url = reverse_lazy("orgmember-list")


class OrgMemberDeleteView(DeleteView):
    model = OrgMember
    template_name = "orgmem_del.html"
    success_url = reverse_lazy("orgmember-list")


class StudentList(ListView):
    model = Student
    context_object_name = "student"
    template_name = "student_list.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(StudentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(
                Q(student_id__icontains=query)
                | Q(lastname__icontains=query)
                | Q(firstname__icontains=query)
                | Q(middlename__icontains=query)
                | Q(program__prog_name__icontains=query)
            )
        return qs


class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = "student_add.html"
    success_url = reverse_lazy("student-list")


class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "student_edit.html"
    success_url = reverse_lazy("student-list")


class StudentDeleteView(DeleteView):
    model = Student
    template_name = "student_del.html"
    success_url = reverse_lazy("student-list")


class CollegeList(ListView):
    model = College
    context_object_name = "college"
    template_name = "college_list.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(CollegeList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(Q(college_name__icontains=query))
        return qs


class CollegeCreateView(CreateView):
    model = College
    form_class = CollegeForm
    template_name = "college_add.html"
    success_url = reverse_lazy("college-list")


class CollegeUpdateView(UpdateView):
    model = College
    form_class = CollegeForm
    template_name = "college_edit.html"
    success_url = reverse_lazy("college-list")


class CollegeDeleteView(DeleteView):
    model = College
    template_name = "college_del.html"
    success_url = reverse_lazy("college-list")


class ProgramList(ListView):
    model = Program
    context_object_name = "program"
    template_name = "program_list.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(ProgramList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get("q")
            qs = qs.filter(
                Q(prog_name__icontains=query)
                | Q(college__college_name__icontains=query)
            )
        return qs


class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm
    template_name = "program_add.html"
    success_url = reverse_lazy("program-list")


class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = "program_edit.html"
    success_url = reverse_lazy("program-list")


class ProgramDeleteView(DeleteView):
    model = Program
    template_name = "program_del.html"
    success_url = reverse_lazy("program-list")


def PieCountbySeverity(request):
    query = """
    SELECT severity_level, COUNT(*) as count
    FROM studentorg_fireincident
    GROUP BY severity_level
    """
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = FireIncident.objects.filter(
        date_time__year=current_year
    ).values_list("date_time", flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):

    query = """
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        studentorg_fireincident fi
    JOIN 
        studentorg_firelocation fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                studentorg_fireincident fi_top
            JOIN 
                studentorg_firelocation fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = """
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        studentorg_fireincident fi
    GROUP BY fi.severity_level, month
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)


def studentsPerProgram(request):
    query = """
        SELECT sp.prog_name, COUNT(ss.id) AS student_count
        FROM studentorg_student ss
        JOIN studentorg_program sp ON ss.program_id = sp.id
        GROUP BY sp.prog_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Convert the result to a list of dictionaries
    result = [{"prog_name": row[0], "student_count": row[1]} for row in rows]

    return JsonResponse(result, safe=False)


def organizationsByCollege(request):
    query = """
        SELECT sc.college_name, COUNT(so.id) AS org_count
        FROM studentorg_organization so
        JOIN studentorg_college sc ON so.college_id = sc.id
        GROUP BY sc.college_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Convert the result to a list of dictionaries
    result = [{"college_name": row[0], "org_count": row[1]} for row in rows]

    return JsonResponse(result, safe=False)


def programEnrollmentDistribution(request):
    query = """
        SELECT sp.prog_name, COUNT(ss.id) AS student_count
        FROM studentorg_student ss
        JOIN studentorg_program sp ON ss.program_id = sp.id
        GROUP BY sp.prog_name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Convert the result to a list of dictionaries
    result = [{"prog_name": row[0], "student_count": row[1]} for row in rows]

    return JsonResponse(result, safe=False)


def studentEnrollmentTrends(request):
    query = """
        SELECT strftime('%Y', created_at) AS year, COUNT(id) AS student_count
        FROM studentorg_student
        GROUP BY year
        ORDER BY year
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    result = [{"year": row[0], "student_count": row[1]} for row in rows]
    return JsonResponse(result, safe=False)


def organizationMembershipDistribution(request):
    query = """
        SELECT so.name AS organization_name, COUNT(som.id) AS member_count
        FROM studentorg_orgmember som
        JOIN studentorg_organization so ON som.organization_id = so.id
        GROUP BY so.name
        ORDER BY member_count DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    result = [{"organization_name": row[0], "member_count": row[1]} for row in rows]
    return JsonResponse(result, safe=False)


# Predefined coordinates for barangays in Puerto Princesa City
barangay_coordinates = {
    "Barangay San Pedro": (9.759001431851921, 118.75786335104155),
    "Barangay Mandaragat": (9.748646551957371, 118.73964419467723),
    "Barangay San Miguel": (9.74757389879427, 118.75642401298171),
    "Barangay San Jose": (9.794098800097737, 118.75921266844219),
    "Barangay Tiniguiban": (9.771414551960454, 118.74452901673914),
    "Barangay San Manuel": (9.771700446692131, 118.76425827599432),
    "Barangay Santa Monica": (9.788931598544831, 118.73093532877895),
    "Barangay Tagburos": (9.822344379670465, 118.74394796348989),
    "Barangay Manggahan": (9.73990456054043, 118.73908841261942),
}


def map_station(request):
    city = request.GET.get("city", None)

    fireStations = FireStation.objects.all()
    fireIncidents = FireIncident.objects.all()

    if city:
        fireStations = fireStations.filter(location__country=city)
        fireIncidents = fireIncidents.filter(location__country=city)

    fireStations_list = list(fireStations.values("name", "latitude", "longitude"))
    for station in fireStations_list:
        station["latitude"] = float(station["latitude"])
        station["longitude"] = float(station["longitude"])

    fireIncidents_list = []
    for incident in fireIncidents:
        if incident.latitude is None or incident.longitude is None:
            barangay_name = incident.location.country.split(",")[
                0
            ].strip()  # Assuming location country stores barangay name
            if barangay_name in barangay_coordinates:
                incident.latitude = random.uniform(
                    barangay_coordinates[barangay_name][0] - 0.008,
                    barangay_coordinates[barangay_name][0] + 0.008,
                )
                incident.longitude = random.uniform(
                    barangay_coordinates[barangay_name][1] - 0.008,
                    barangay_coordinates[barangay_name][1] + 0.008,
                )
            else:
                # Generate random coordinates within the initial map view bounds as a fallback
                incident.latitude = random.uniform(9.805, 9.828)
                incident.longitude = random.uniform(118.710, 118.740)
            incident.save()

        fireIncidents_list.append(
            {
                "date_time": incident.date_time.isoformat(),
                "severity_level": incident.severity_level,
                "latitude": float(incident.latitude),
                "longitude": float(incident.longitude),
                "location_country": incident.location.country,
            }
        )

    cities = FireLocation.objects.values_list("country", flat=True).distinct()

    context = {
        "fireStations": fireStations_list,
        "fireIncidents": json.dumps(fireIncidents_list),
        "cities": cities,
        "selected_city": city,
    }

    return render(request, "mapstation.html", context)
