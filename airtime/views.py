import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Provider, Transaction, DataBundle
from .forms import AirtimePurchaseForm, DataPurchaseForm
from django.shortcuts import render, redirect

# Utility Functions
def load_json_file(file_path):
    """
    Load a JSON file from the specified path.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def paga_api_request(endpoint, payload):
    """
    Make a request to the Paga API.
    """
    api_base_url = settings.PAGA_API_BASE_URL
    api_key = settings.PAGA_API_KEY
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        response = requests.post(f"{api_base_url}/{endpoint}", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


# Views
def providers_view(request):
    """
    Display the list of available ISPs.
    """
    providers = Provider.objects.all()
    return render(request, "airtime/providers.html", {"providers": providers})


def data_bundles_view(request, provider):
    """
    Display available data bundles for the selected provider.
    """
    try:
        provider_obj = Provider.objects.get(name__iexact=provider)
    except Provider.DoesNotExist:
        messages.error(request, "Invalid provider selected.")
        return redirect("providers")

    bundles = DataBundle.objects.filter(provider=provider_obj)
    return render(request, "airtime/data_bundles.html", {
        "provider": provider_obj,
        "bundles": bundles,
    })


@csrf_exempt
def purchase_airtime_view(request):
    """
    Handle airtime purchase for any provider.
    """
    if request.method == "POST":
        form = AirtimePurchaseForm(request.POST)
        if form.is_valid():
            airtime_purchase = form.save(commit=False)
            airtime_purchase.user = request.user

            # Prepare payload for the Paga API
            payload = {
                "service": "airtime",
                "provider": airtime_purchase.provider.paga_provider_id,
                "phone_number": airtime_purchase.phone_number,
                "amount": airtime_purchase.amount,
            }
            response = paga_api_request("purchase", payload)

            if "error" in response:
                messages.error(request, f"Purchase failed: {response['error']}")
            else:
                airtime_purchase.transaction_id = response.get("transaction_id", "")
                airtime_purchase.save()

                # Record transaction
                Transaction.objects.create(
                    user=request.user,
                    provider=airtime_purchase.provider,
                    transaction_type="Airtime",
                    amount=airtime_purchase.amount,
                    reference=airtime_purchase.transaction_id,
                )
                messages.success(request, "Airtime purchase successful!")
        else:
            messages.error(request, "Form submission failed. Please correct the errors.")

    form = AirtimePurchaseForm()
    return render(request, "airtime/purchase_airtime.html", {"form": form})


@csrf_exempt
def purchase_data_view(request, provider):
    """
    Handle data bundle purchase for a selected ISP.
    """
    if request.method == "POST":
        form = DataPurchaseForm(request.POST)
        if form.is_valid():
            data_purchase = form.save(commit=False)
            data_purchase.user = request.user

            # Prepare payload for the Paga API
            payload = {
                "service": "data",
                "provider": data_purchase.provider.paga_provider_id,
                "phone_number": data_purchase.phone_number,
                "bundle_code": data_purchase.bundle.bundle_code,
            }
            response = paga_api_request("purchase", payload)

            if "error" in response:
                messages.error(request, f"Purchase failed: {response['error']}")
            else:
                data_purchase.transaction_id = response.get("transaction_id", "")
                data_purchase.save()

                # Record transaction
                Transaction.objects.create(
                    user=request.user,
                    provider=data_purchase.provider,
                    transaction_type="Data Bundle",
                    amount=data_purchase.bundle.price,
                    reference=data_purchase.transaction_id,
                )
                messages.success(request, "Data bundle purchase successful!")
        else:
            messages.error(request, "Form submission failed. Please correct the errors.")

    provider_obj = Provider.objects.get(name__iexact=provider)
    bundles = DataBundle.objects.filter(provider=provider_obj)
    form = DataPurchaseForm(initial={"provider": provider_obj})
    return render(request, "airtime/purchase_data.html", {"form": form, "bundles": bundles})


def api_data_bundles(request, provider):
    """
    Provide available data bundles as an API endpoint.
    """
    try:
        provider_obj = Provider.objects.get(name__iexact=provider)
        bundles = DataBundle.objects.filter(provider=provider_obj)
        response = [{"id": bundle.id, "name": bundle.name, "price": bundle.price, "code": bundle.bundle_code} for bundle in bundles]
        return JsonResponse(response, safe=False)
    except Provider.DoesNotExist:
        return JsonResponse({"error": "Invalid provider"}, status=404)


@login_required
def transaction_history(request):
    """
    Display the transaction history for the logged-in user.
    """
    transactions = Transaction.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "airtime/transaction_history.html", {"transactions": transactions})


# @login_required
# def update_profile(request):
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             # Log the profile update
#             ActivityLog.objects.create(
#                 user=request.user,
#                 action='profile_update',
#                 description='User updated their profile.'
#             )
#             return redirect('profile')
#     else:
#         form = ProfileUpdateForm(instance=request.user)

#     return render(request, 'users/update_profile.html', {'form': form})