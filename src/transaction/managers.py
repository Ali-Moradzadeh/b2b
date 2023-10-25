from django.db.models import Manager, QuerySet, Sum, Q


processed_q = Q(processed=True)


class CreditChargeRequestBaseManager(Manager):
    def total_charges_of(self, user_id):
        total = self.filter(wallet__profile__user__id=user_id).aggregate(Sum("amount")).get("amount__sum", 0)
        return total if total else 0


class CreditChargeRequestManager(CreditChargeRequestBaseManager):
    def total_processed_charges_of(self, user_id):
        total = self.filter(Q(wallet__profile__user__id=user_id) & processed_q).aggregate(Sum("amount")).get("amount__sum", 0)
        return total if total else 0
    
    def total_not_processed_charges_of(self, user_id):
        total = self.filter(Q(wallet__profile__user__id=user_id) & ~processed_q).aggregate(Sum("amount")).get("amount__sum", 0)
        return total if total else 0
    

class ProcessedCreditChargeRequestManager(CreditChargeRequestBaseManager):
    def get_queryset(self):
        return QuerySet(self.model, self._db).filter(processed_q)


class NotProcessedCreditChargeRequestManager(CreditChargeRequestBaseManager):
    def get_queryset(self):
        return QuerySet(self.model, self._db).filter(~processed_q)


class SellCreditManager(Manager):
    def total_sells_of(self, user_id):
        total = self.filter(wallet__profile__user__id=user_id).aggregate(Sum("amount")).get("amount__sum", 0)
        return total if total else 0