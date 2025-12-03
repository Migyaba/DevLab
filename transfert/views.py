from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import execute_p2p_transfer_via_sdk 
from .models import Account, Transfer
from .serializers import P2PTransferSerializer

class P2PTransferAPIView(APIView):
    
    def post(self, request):
        serializer = P2PTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            sender_account = Account.objects.get(msisdn=data['sender_msisdn'])
        except Account.DoesNotExist:
            return Response({"error": "Sender account not found in local DB."}, status=status.HTTP_404_NOT_FOUND)

        sdk_result = execute_p2p_transfer_via_sdk(
            sender_msisdn=sender_account.msisdn,
            receiver_msisdn=data['receiver_msisdn'],
            amount=data['amount'],
            note=data.get('note', '')
        )
        
        # Enregistrement de la trace locale (succès ou échec)
        new_transfer = Transfer.objects.create(
            sender=sender_account,
            receiver_msisdn=data['receiver_msisdn'],
            amount=data['amount'],
            transfer_id=sdk_result.get('transfer_id'),
            home_transaction_id=sdk_result['home_transaction_id'],
            status='MOJALOOP_COMPLETED' if sdk_result['success'] else 'FAILED',
            sdk_response_data=sdk_result.get('data') or sdk_result # Enregistre la réponse JSON ou l'erreur
        )

        if sdk_result['success']:
            return Response({
                "message": "Mojaloop P2P Transfer COMPLETED.",
                "transfer_id": new_transfer.transfer_id,
                "status": new_transfer.status,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Mojaloop P2P Transfer FAILED.",
                "details": sdk_result['error'],
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)