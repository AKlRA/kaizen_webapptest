from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone


class Image(models.Model):
    image = models.ImageField(upload_to='kaizen_images/')
    description = models.TextField(blank=True)

class KaizenSheet(models.Model):
    title = models.CharField(max_length=255, unique=True)
    area_implemented = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    problem = models.TextField()
    idea_solved = models.TextField()
    standardization = models.TextField()
    benefits = models.TextField()
    deployment = models.TextField()
    is_temporary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    project_leader = models.CharField(max_length=255, blank=True, null=True)  # Make nullable
    team_member1_id = models.CharField(max_length=50, blank=True, null=True)
    team_member1 = models.CharField(max_length=255, blank=True, null=True)
    team_member2_id = models.CharField(max_length=50, blank=True, null=True)
    team_member2 = models.CharField(max_length=255, blank=True, null=True)
    
    savings_start_month = models.CharField(max_length=20, blank=True, null=True)  # Changed from DateField
    estimated_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    realized_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    handwritten_sheet = models.ImageField(
        upload_to='kaizen/handwritten/',
        blank=True,
        null=True,
        verbose_name='Handwritten Kaizen Sheet'
    )
    is_handwritten = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('hod_approved', 'HOD Approved'),
        ('finance_pending', 'Finance Review Pending'),
        ('finance_approved', 'Finance Approved'),
        ('finance_rejected', 'Finance Rejected'),
        ('coordinator_approved', 'Fully Approved'),
    ]
    
    approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    hod_approved = models.BooleanField(default=False)
    coordinator_approved = models.BooleanField(default=False)
    hod_approved_at = models.DateTimeField(null=True, blank=True)
    coordinator_approved_at = models.DateTimeField(null=True, blank=True)
    hod_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_approved_sheets'
    )
    coordinator_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinator_approved_sheets'
    )

    finance_approved = models.BooleanField(default=False)
    finance_approved_at = models.DateTimeField(null=True, blank=True)
    finance_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finance_approved_sheets'
    )

    
    @property
    def is_editable(self):
        return self.approval_status == 'pending'
    
    @property
    def get_approval_status_display(self):
        if self.approval_status == 'coordinator_approved':
            return 'Approved'
        elif self.approval_status == 'hod_approved':
            return 'Coordinator Approval Pending'
        elif self.approval_status == 'pending':
            return 'No Approval'
        return 'Rejected'


    def needs_finance_approval(self):
        try:
            cost_before = float(self.cost_before_implementation or 0)
            cost_after = float(self.cost_after_implementation or 0)
            return abs(cost_before - cost_after) > 100000
        except ValueError:
            return False

    def approve_by_hod(self, hod_user):
        self.hod_approved = True
        self.hod_approved_by = hod_user
        self.hod_approved_at = timezone.now()
        
        # Update status based on handwritten or cost
        if self.is_handwritten or (45000 < self.get_cost_difference() <= 100000):
            self.approval_status = 'coordinator_pending'
        else:
            self.approval_status = 'completed'
        
        self.save()

    def approve_by_finance(self, finance_user):
        if self.approval_status == 'finance_pending':
            self.finance_approved = True
            self.finance_approved_by = finance_user
            self.finance_approved_at = datetime.now()
            self.approval_status = 'finance_approved'  # Set to finance_approved
            self.save()

    def reject_by_finance(self, finance_user):
        if self.approval_status == 'finance_pending':
            self.finance_approved = False
            self.finance_approved_by = finance_user
            self.finance_approved_at = datetime.now()
            self.approval_status = 'finance_rejected'  # Set to finance_rejected
            self.save()

    def approve_by_coordinator(self, coordinator_user):
        # Check if sheet needs finance approval
        if self.needs_finance_approval():
            if self.approval_status == 'hod_approved':
                self.approval_status = 'finance_pending'
                self.save()
                return
            elif self.approval_status != 'finance_approved':
                return
        
        # If no finance approval needed or already finance approved
        self.coordinator_approved = True
        self.coordinator_approved_by = coordinator_user
        self.coordinator_approved_at = datetime.now()
        self.approval_status = 'coordinator_approved'
        self.save()

    def get_cost_difference(self):
        try:
            before = float(self.cost_before_implementation or 0)
            after = float(self.cost_after_implementation or 0)
            return abs(before - after)
        except (ValueError, TypeError):
            return 0

    def needs_finance_approval(self):
        return self.get_cost_difference() > 100000

    def needs_coordinator_approval(self):
        # Add condition for handwritten sheets
        if self.is_handwritten:
            return True
        cost_diff = self.get_cost_difference()
        return 45000 < cost_diff <= 100000

    def needs_only_hod_approval(self):
        # Handwritten sheets need both HOD and coordinator approval
        if self.is_handwritten:
            return False
        return 0 < self.get_cost_difference() <= 45000

    def get_approval_status_display(self):
        try:
            # Add handwritten sheet logic
            if self.is_handwritten:
                if not self.hod_approved:
                    return "HOD Approval Pending"
                return "Completed" if self.coordinator_approved else "Coordinator Approval Pending"
            
            cost_diff = self.get_cost_difference()
            
            if cost_diff == 0 and not self.is_handwritten:
                return "No approval needed"
                
            if cost_diff <= 45000 and not self.is_handwritten:
                return "Completed" if self.hod_approved else "HOD Approval Pending"
                
            if cost_diff <= 100000 or self.is_handwritten:
                if not self.hod_approved:
                    return "HOD Approval Pending"
                return "Completed" if self.coordinator_approved else "Coordinator Approval Pending"
                
            # Above 100k
            if not self.hod_approved:
                return "HOD Approval Pending"
            if not self.finance_approved:
                return "Finance Approval Pending"
            if not self.coordinator_approved:
                return "Coordinator Approval Pending"
            return "Completed"
            
        except (ValueError, TypeError):
            return "Invalid Cost Values"

    def get_available_departments(self):
        return Profile.objects.filter(
            user_type='hod'
        ).exclude(
            department=self.employee.profile.department
        ).values_list('department', flat=True)    
    # Serial Key - unique and auto-generated
    serial_key = models.CharField(max_length=15, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.serial_key:
            self.serial_key = self.generate_serial_key()
        super().save(*args, **kwargs)

    def generate_serial_key(self):
        current_year = datetime.now().year
        year_suffix = str(current_year)[-2:]
        latest_kaizen = KaizenSheet.objects.all().order_by('id').last()

        if latest_kaizen and latest_kaizen.serial_key:
            try:
                last_number = int(latest_kaizen.serial_key.split('-')[-1])
            except ValueError:
                last_number = 0
            new_number = f'{last_number + 1:04d}'
        else:
            new_number = '0001'

        serial_key = f'KAI-{year_suffix}-{new_number}'
        return serial_key

    before_improvement_image = models.ImageField(upload_to='kaizen/before/', blank=True, null=True)
    after_improvement_image = models.ImageField(upload_to='kaizen/after/', blank=True, null=True)

    impacts_safety = models.BooleanField(default=False)
    impacts_quality = models.BooleanField(default=False)
    impacts_productivity = models.BooleanField(default=False)
    impacts_delivery = models.BooleanField(default=False)
    impacts_cost = models.BooleanField(default=False)
    impacts_morale = models.BooleanField(default=False)
    impacts_environment = models.BooleanField(default=False)

    safety_benefits_description = models.TextField(blank=True, null=True)
    safety_uom = models.CharField(max_length=255, blank=True, null=True)
    safety_before_implementation = models.TextField(blank=True, null=True)
    safety_after_implementation = models.TextField(blank=True, null=True)
    
    quality_benefits_description = models.TextField(blank=True, null=True)
    quality_uom = models.CharField(max_length=255, blank=True, null=True)
    quality_before_implementation = models.TextField(blank=True, null=True)
    quality_after_implementation = models.TextField(blank=True, null=True)
    
    productivity_benefits_description = models.TextField(blank=True, null=True)
    productivity_uom = models.CharField(max_length=255, blank=True, null=True)
    productivity_before_implementation = models.TextField(blank=True, null=True)
    productivity_after_implementation = models.TextField(blank=True, null=True)
    
    delivery_benefits_description = models.TextField(blank=True, null=True)
    delivery_uom = models.CharField(max_length=255, blank=True, null=True)
    delivery_before_implementation = models.TextField(blank=True, null=True)
    delivery_after_implementation = models.TextField(blank=True, null=True)
    
    cost_benefits_description = models.TextField(blank=True, null=True)
    cost_uom = models.CharField(max_length=255, blank=True, null=True)
    cost_before_implementation = models.TextField(blank=True, null=True)
    cost_after_implementation = models.TextField(blank=True, null=True)
    
    morale_benefits_description = models.TextField(blank=True, null=True)
    morale_uom = models.CharField(max_length=255, blank=True, null=True)
    morale_before_implementation = models.TextField(blank=True, null=True)
    morale_after_implementation = models.TextField(blank=True, null=True)
    
    environment_benefits_description = models.TextField(blank=True, null=True)
    environment_uom = models.CharField(max_length=255, blank=True, null=True)
    environment_before_implementation = models.TextField(blank=True, null=True)
    environment_after_implementation = models.TextField(blank=True, null=True)

    before_improvement_text = models.TextField(blank=True, null=True)
    after_improvement_text = models.TextField(blank=True, null=True)
    
    cost_calculation = models.FileField(
        upload_to='kaizen/cost_calculations/',
        blank=True,
        null=True,
        verbose_name='Cost Calculation File'
    )

    standardization_file = models.FileField(
        upload_to='kaizen/standardization/',
        blank=True,
        null=True
    )
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kaizen_sheets_created')
    implemented_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='kaizen_sheets_implemented')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Kaizen Sheet: {self.title} by {self.employee.username}"

    
# models.py
class Profile(models.Model):
    DEPARTMENT_CHOICES = [
        ('CORPORATE - GENERAL', 'CORPORATE - GENERAL'),
        ('SCM - CONVEYOR DESIGN & ASSEMBLY', 'SCM - CONVEYOR DESIGN & ASSEMBLY'),
        ('SUPPLY CHAIN MANAGEMENT', 'SUPPLY CHAIN MANAGEMENT'),
        ('ASSEMBLY MECH - HMC', 'ASSEMBLY MECH - HMC'),
        ('SCM - LOGISTICS', 'SCM - LOGISTICS'),
        ('ASSEMBLY MECH - VMC', 'ASSEMBLY MECH - VMC'),
        ('ASSEMBLY', 'ASSEMBLY'),
        ('TSG - MARKETING TOOLED UP MACHINES', 'TSG - MARKETING TOOLED UP MACHINES'),
        ('STORES - MECH', 'STORES - MECH'),
        ('FA - SUB ASSEMBLY', 'FA - SUB ASSEMBLY'),
        ('PACKING & DISPATCH', 'PACKING & DISPATCH'),
        ('METHODS ENGINEERING', 'METHODS ENGINEERING'),
        ('L & D - TECHNICAL TRAINER', 'L & D - TECHNICAL TRAINER'),
        ('SCM - PURCHASE B/O & IMPORTS', 'SCM - PURCHASE B/O & IMPORTS'),
        ('MACHINE SHOP', 'MACHINE SHOP'),
        ('DESIGN & DEVELOPMENT', 'DESIGN & DEVELOPMENT'),
        ('BB - SUB ASSEMBLY - HEADSTOCK & INDEX TABLE', 'BB - SUB ASSEMBLY - HEADSTOCK & INDEX TABLE'),
        ('PLANT MAINTENANCE', 'PLANT MAINTENANCE'),
        ('ELECTRICAL - DESIGN', 'ELECTRICAL - DESIGN'),
        ('QUALITY', 'QUALITY'),
        ('ELECTRICAL - LINE ASSEMBLY', 'ELECTRICAL - LINE ASSEMBLY'),
        ('ACCOUNTS & ADMIN', 'ACCOUNTS & ADMIN'),
        ('FA - SUB ASSEMBLY - PNEUMATIC', 'FA - SUB ASSEMBLY - PNEUMATIC'),
        ('BB - SUB ASSEMBLY', 'BB - SUB ASSEMBLY'),
        ('ELECTRICAL - CABINET ASSEMBLY', 'ELECTRICAL - CABINET ASSEMBLY'),
        ('ASSEMBLY MECH - VMC - LAPC', 'ASSEMBLY MECH - VMC - LAPC'),
        ('LINE ASSEMBLY', 'LINE ASSEMBLY'),
        ('TRYOUTS', 'TRYOUTS'),
        ('TSG - SALES EXECUTION', 'TSG - SALES EXECUTION'),
        ('SCM - SPARES SUPPLY', 'SCM - SPARES SUPPLY'),
        ('PPC', 'PPC'),
        ('ELECTRICAL - PLANNING', 'ELECTRICAL - PLANNING'),
        ('CSG', 'CSG'),
        ('TSG - APPLICATION ENGINEERING', 'TSG - APPLICATION ENGINEERING'),
        ('PAINT SHOP', 'PAINT SHOP'),
        ('TSG - EXPORTS', 'TSG - EXPORTS'),
        ('FIXTURE DESIGN', 'FIXTURE DESIGN'),
        ('ASSEMBLY MECH - VMC - RAPC', 'ASSEMBLY MECH - VMC - RAPC'),
        ('R & D', 'R & D'),
        ('ELECTRICAL - ASSEMBLY', 'ELECTRICAL - ASSEMBLY'),
        ('EXPORT ASSEMBLY', 'EXPORT ASSEMBLY'),
        ('ELECTRICAL - PROCUREMENT', 'ELECTRICAL - PROCUREMENT'),
        ('BB - SUB ASSEMBLY - ROTARY APC', 'BB - SUB ASSEMBLY - ROTARY APC'),
        ('FA - SUB ASSEMBLY - DISC & GRIPPER ARM', 'FA - SUB ASSEMBLY - DISC & GRIPPER ARM'),
        ('HRD', 'HRD'),
        ('SA - FIXTURE', 'SA - FIXTURE'),
        ('SCM - PROCESS ENGINEERING - MANUFACTURING EXCELLENCE', 'SCM - PROCESS ENGINEERING - MANUFACTURING EXCELLENCE'),
        ('PROJECTS', 'PROJECTS'),
        ('TSG - DIE & MOULD', 'TSG - DIE & MOULD'),
        ('TSG - BUSINESS DEVELOPMENT', 'TSG - BUSINESS DEVELOPMENT'),
        ('SCM - SHEETMETAL PROCUREMENT', 'SCM - SHEETMETAL PROCUREMENT'),
        ('BB - SUB ASSEMBLY - LINEAR APC', 'BB - SUB ASSEMBLY - LINEAR APC'),
        ('BB - SUB ASSEMBLY - SPINDLE', 'BB - SUB ASSEMBLY - SPINDLE'),
        ('SCM - PATTERN & CASTING', 'SCM - PATTERN & CASTING'),
        ('ISG - HARDWARE & NETWORKING', 'ISG - HARDWARE & NETWORKING'),
        ('FA - SUB ASSEMBLY - FRONT ATC', 'FA - SUB ASSEMBLY - FRONT ATC'),
        ('BB - SUB ASSEMBLY - ROTARY TABLE & CONE ASSEMBLY', 'BB - SUB ASSEMBLY - ROTARY TABLE & CONE ASSEMBLY'),
        ('SCM - B & C CLASS FOE', 'SCM - B & C CLASS FOE'),
        ('SCM - DIGITAL SAP AMALGAMATION', 'SCM - DIGITAL SAP AMALGAMATION'),
        ('SCM - MANUFACTURING', 'SCM - MANUFACTURING'),
        ('BB - SUB ASSEMBLY - SLIDE PALLET LAPC/RAPC', 'BB - SUB ASSEMBLY - SLIDE PALLET LAPC/RAPC'),
        ('BB - SUB ASSEMBLY - BALLSCREW', 'BB - SUB ASSEMBLY - BALLSCREW'),
        ('TSG - MARKETING', 'TSG - MARKETING'),
        ('BASE BUILD - AMS 2', 'BASE BUILD - AMS 2'),
        ('FA - SUB ASSEMBLY - COOLANT SYSTEMS', 'FA - SUB ASSEMBLY - COOLANT SYSTEMS'),
        ('ELECTRICAL - SUB ASSEMBLY', 'ELECTRICAL - SUB ASSEMBLY'),
        ('STORES', 'STORES'),
        ('SCM - COSTING & INVENTORY CONTROL', 'SCM - COSTING & INVENTORY CONTROL'),
        ('SCM - A CLASS MANUFACTURING', 'SCM - A CLASS MANUFACTURING'),
        ('TSG - AEROSPACE', 'TSG - AEROSPACE'),
        ('TSG - AUTOMATION', 'TSG - AUTOMATION'),
        ('EEP', 'EEP'),
        ('ELECTRICAL - NAPC', 'ELECTRICAL - NAPC'),
        ('ELECTRICAL - RAPC', 'ELECTRICAL - RAPC'),
        ('ELECTRICAL - LARGE VMC', 'ELECTRICAL - LARGE VMC'),
        ('ELECTRICAL - LARGE HMC', 'ELECTRICAL - LARGE HMC'),
        ('TSG - MARKETING - TENDERS', 'TSG - MARKETING - TENDERS'),
        ('ELECTRICAL - EXPORT', 'ELECTRICAL - EXPORT'),
    ]

    # Rest of Profile model remains same

    USER_TYPES = (
        ('employee', 'Employee'),
        ('coordinator', 'Coordinator'),
        ('hod', 'Hod'),
        ('finance', 'Finance and Accounts')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPES,
        default='employee'
    )
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,  # Allow null temporarily
        blank=True,  # Allow blank temporarily
        help_text="Unique employee identification number"
    )

    @property
    def is_coordinator(self):
        return self.user_type == 'coordinator'
    
    @property
    def is_employee(self):
        return self.user_type == 'employee'
    
    @property
    def is_hod(self):
        return self.user_type == 'hod'

    @property
    def is_finance(self):
        return self.user_type == 'finance'

    def __str__(self):
        return f"{self.user.username}'s profile"
    
# models.py
class HorizontalDeployment(models.Model):
    kaizen_sheet = models.ForeignKey(KaizenSheet, on_delete=models.CASCADE, related_name='deployments')
    department = models.CharField(max_length=100)
    deployed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('kaizen_sheet', 'department')

    def __str__(self):
        return f"{self.kaizen_sheet.title} - {self.department}"
    

class KaizenCoordinator(models.Model):
    department = models.CharField(max_length=100, unique=True)
    coordinator_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.department} - {self.coordinator_name or 'No Coordinator'}"       
