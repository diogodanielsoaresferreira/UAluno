from django import forms

class NotaForm(forms.Form):
    nome_cadeira = forms.CharField(label='nomecadeira', widget=forms.TextInput())
    ects = forms.IntegerField(label='ects', widget=forms.TextInput(), min_value=1, max_value=30)
    area = forms.CharField(label='area', widget=forms.TextInput())
    ano = forms.IntegerField(label='ano', widget=forms.TextInput(), min_value=0, max_value=5)
    semestre = forms.IntegerField(label='semestre', widget=forms.TextInput(), min_value=0, max_value=2)
    nota = forms.IntegerField(label='nota', widget=forms.TextInput(), max_value=20, min_value=0)