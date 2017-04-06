from django.db import models


class Diner(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=160, default='')
    employee_number = models.CharField(max_length=32, default='')
    RFID = models.CharField(default='', max_length=24)

    class Meta:
        verbose_name = 'Comensal'
        verbose_name_plural = 'Comensales'

    def __str__(self):
        return self.name

class AccessLog(models.Model):
    diner = models.ForeignKey(Diner, null=True, blank=True)
    RFID = models.CharField(default='', max_length=24)
    access_to_room = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Control de Acceso'
        verbose_name_plural = 'Control de Accesos'

    def __str__(self):
        return self.RFID


class ElementScore(models.Model):
    element = models.CharField(max_length=48, default='', unique=True)

    class Meta:
        verbose_name = "Elemento a valorar"
        verbose_name_plural = "Elementos a valorar"

    def __str__(self):
        return self.element


class Score(models.Model):
    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def __str__(self):
        pass
    
