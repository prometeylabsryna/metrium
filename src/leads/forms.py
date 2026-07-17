from django import forms


class PhoneLeadForm(forms.Form):
    tel = forms.CharField(max_length=30)
    loc = forms.CharField(max_length=500, required=False)
    channel = forms.CharField(max_length=40, required=False)


class CalculatorLeadForm(forms.Form):
    name = forms.CharField(max_length=200)
    tel = forms.CharField(max_length=30)
    type = forms.CharField(max_length=100, required=False)
    square = forms.CharField(max_length=50, required=False)
    price = forms.CharField(max_length=100, required=False)
    region = forms.CharField(max_length=200, required=False)
    cityInput = forms.CharField(max_length=200, required=False)
    plan = forms.CharField(max_length=200, required=False)


class ReviewLeadForm(forms.Form):
    name = forms.CharField(max_length=200)
    comment = forms.CharField()
    rate = forms.CharField(max_length=20)
    loc = forms.CharField(max_length=500, required=False)
