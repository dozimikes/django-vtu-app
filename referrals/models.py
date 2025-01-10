# from django.db import models
# from django.conf import settings
# from django.utils.timezone import now


# class Referral(models.Model):
#     """
#     Model to track referrals.
#     """
#     referrer = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="referrals"
#     )
#     referred = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="referred"
#     )
#     referred_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.referrer.username} referred {self.referred.username}"


# class Reward(models.Model):
#     """
#     Model to track rewards for referrals.
#     """
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="rewards"
#     )
#     points = models.PositiveIntegerField()
#     reason = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.points} points"
