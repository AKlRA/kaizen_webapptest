from django import forms
from django.contrib.auth.models import User
from .models import KaizenSheet, Image, Profile

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('employee', 'Employee'), ('hod', 'Hod'), ('coordinator', 'Coordinator'), ('finance', 'Finance and Accounts')])
    department = forms.ChoiceField(choices=Profile.DEPARTMENT_CHOICES)
    employee_id = forms.CharField(max_length=50)


    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'employee_id', 'user_type', 'department']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        employee_id = cleaned_data.get("employee_id")


        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        if Profile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("This Employee ID is already in use")        

        return cleaned_data

class KaizenSheetForm(forms.ModelForm):
    before_improvement_image = forms.ImageField(required=False)
    after_improvement_image = forms.ImageField(required=False)

    class Meta:
        model = KaizenSheet
        fields = [
            'title', 'area_implemented', 'start_date', 'end_date',
            'problem', 'idea_solved', 'standardization', 'benefits',
            'deployment', 
            # Team member fields - only team member 2 as employee is team member 1
            'team_member2_id', 'team_member2',
            # Impact fields
            'impacts_safety', 'impacts_quality', 'impacts_productivity',
            'impacts_delivery', 'impacts_cost', 'impacts_morale', 'impacts_environment',
            'safety_benefits_description', 'safety_uom',
            'safety_before_implementation', 'safety_after_implementation',
            'quality_benefits_description', 'quality_uom', 'quality_before_implementation',
            'quality_after_implementation', 'productivity_benefits_description',
            'productivity_uom', 'productivity_before_implementation',
            'productivity_after_implementation', 'delivery_benefits_description',
            'delivery_uom', 'delivery_before_implementation',
            'delivery_after_implementation', 'cost_benefits_description',
            'cost_uom', 'cost_before_implementation', 'cost_after_implementation',
            'morale_benefits_description', 'morale_uom', 'morale_before_implementation',
            'morale_after_implementation', 'environment_benefits_description',
            'environment_uom', 'environment_before_implementation',
            'environment_after_implementation', 'before_improvement_text',
            'after_improvement_text', 'standardization_file',
            'before_improvement_image', 'after_improvement_image', 'cost_calculation',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            
            # Handle horizontal departments
            if 'horizontal_departments' in self.cleaned_data:
                departments = self.cleaned_data['horizontal_departments']
                if departments:
                    instance.horizontal_departments = ','.join(departments)
                else:
                    instance.horizontal_departments = ''
            
            # Handle images
            if 'before_improvement_image' in self.files:
                img = Image.objects.create(image=self.files['before_improvement_image'])
                instance.before_improvement_images.add(img)
            if 'after_improvement_image' in self.files:
                img = Image.objects.create(image=self.files['after_improvement_image'])
                instance.after_improvement_images.add(img)
                
        return instance
    
# forms.py
class HandwrittenKaizenForm(forms.ModelForm):
    class Meta:
        model = KaizenSheet
        fields = ['title', 'handwritten_sheet']
        
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('handwritten_sheet'):
            raise forms.ValidationError("Handwritten sheet is required")
        return cleaned_data