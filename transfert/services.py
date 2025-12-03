import requests
import uuid
import json

# L'URL de votre SDK Scheme Adapter
SDK_URL = "http://localhost:4001" 

def execute_p2p_transfer_via_sdk(sender_msisdn, receiver_msisdn, amount, note, home_transaction_id=None):
    """
    Exécute le flux Mojaloop complet (Parties, Quote, Transfer) via le SDK /transfers endpoint.
    """
    
    if home_transaction_id is None:
        home_transaction_id = uuid.uuid4()
    
    payload = {
        "from": {
            "displayName": "Django DFSP Client",
            "idType": "MSISDN", 
            "idValue": sender_msisdn
        },
        "to": {
            "idType": "MSISDN",
            "idValue": receiver_msisdn
        },
        "amountType": "SEND",
        "currency": "USD", # IMPORTANT: Doit correspondre à la configuration TTK/SDK
        "amount": str(amount),
        "transactionType": "TRANSFER",
        "note": note,
        "homeTransactionId": str(home_transaction_id)
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(f"{SDK_URL}/transfers", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        sdk_data = response.json()
        
        return {
            "success": True,
            "transfer_id": sdk_data.get('transferId'),
            "status": sdk_data.get('currentState'),
            "data": sdk_data,
            "home_transaction_id": str(home_transaction_id)
        }
    
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de connexion, timeout, ou erreurs 4xx/5xx du SDK
        error_text = getattr(e.response, 'text', str(e))
        return {
            "success": False, 
            "error": f"SDK Request Failed: {error_text}",
            "home_transaction_id": str(home_transaction_id)
        }