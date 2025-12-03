from rest_framework import serializers

class P2PTransferSerializer(serializers.Serializer):
    sender_msisdn = serializers.CharField(max_length=15)
    receiver_msisdn = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True)