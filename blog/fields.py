from django import forms


class SimpleCaptchaField(forms.CharField):

    def __init__(self, label='合言葉の確認', **kwargs):
        super().__init__(label=label, required=True, **kwargs)
        self.widget.attrs['placeholder'] = '天地を？'

    def clean(self, value):
        value = super().clean(value)
        if value == 'こがす' or value == '焦がす':
            return value
        else:
            raise forms.ValidationError('答えが違います')