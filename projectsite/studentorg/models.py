from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class College(BaseModel):
    college_name = models.CharField(max_length=150)

    def __str__(self):
        return self.college_name


class Program(BaseModel):
    prog_name = models.CharField(max_length=150)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return self.prog_name


class Organization(BaseModel):
    name = models.CharField(max_length=150)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Student(BaseModel):
    student_id = models.CharField(max_length=15)
    lastname = models.CharField(max_length=25)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=25, blank=True, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.lastname}, {self.firstname}"


class OrgMember(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    date_joined = models.DateField()


class FireLocation(BaseModel):
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.country


class FireIncident(BaseModel):
    date_time = models.DateTimeField()
    severity_level = models.CharField(max_length=50)
    location = models.ForeignKey(FireLocation, on_delete=models.CASCADE)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    def __str__(self):
        return f"{self.date_time} - {self.severity_level}"


class FireStation(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    location = models.ForeignKey(
        FireLocation, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name
