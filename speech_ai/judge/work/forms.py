from django import forms
from ..models import SpeechContestApplication

        
class SpeechContestApplicationForm(forms.ModelForm):
    class Meta:
        model = SpeechContestApplication
        fields = ['applicant_name', 'applicant_mobile', 'applicant_email', 'speech_content', 'organization', 'speech_file']
