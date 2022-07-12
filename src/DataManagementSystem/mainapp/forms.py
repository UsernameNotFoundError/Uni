from django.forms import ModelForm, TextInput, URLField, ImageField, CharField,\
    PasswordInput
from mainapp.models import Species, Assembly, UserProfileInfo
from django.contrib.auth.models import User

# The form class.
class UserProfileInfoForm(ModelForm):
    class Meta():
        """docstring for Meta.  """
        model = UserProfileInfo
        fields = ('portfolio_site','profile_pic')


class UserLoginForm(ModelForm):
    password = CharField(widget=PasswordInput())
    class Meta():
        model = User
        fields = ('username', 'email', 'password',)



class SpeciesForm(ModelForm):
    """Species form"""
    class Meta:
        model = Species
        exclude = ['image_path']
        widgets = {
            'ncbi_id': TextInput(attrs={'type':'number','class': 'form-control'}),
            'species_name': TextInput(attrs={'class': 'form-control'}),
            'species_code': TextInput(attrs={'class': 'form-control'}),
            'alias': TextInput(attrs={'class': 'form-control'}),
            'category': TextInput(attrs={'class': 'form-control'}),
            'commun_name': TextInput(attrs={'class': 'form-control'}),
            'taxonomy': TextInput(attrs={'class': 'form-control'}),
        }

class AssemblyForm(ModelForm):
    """Assembly Form"""
    class Meta:
        model = Assembly
        exclude = ['dir_location','file_location']
        widgets = {
            'species': TextInput(attrs={'class': 'form-control'}),
            'assembly_id': TextInput(attrs={'type':'number','class': 'form-control'}),
            'assembly_version': TextInput(attrs={'type':'number','class': 'form-control'}),
            'assembly_source': TextInput(attrs={'class': 'form-control'}),
            'addditional_notes': TextInput(attrs={'class': 'form-control'}),
        }  # Check species again
