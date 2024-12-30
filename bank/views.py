from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction
from django.contrib import messages
from .forms import CustomUserCreationForm, UserUpdateForm
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import User
from .forms import CashWithdrawalForm

def index(request):
    return render(request, 'templates/index.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, "Your account has been created successfully!")
            return redirect('login')
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'templates/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')

        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'templates/login.html', {'form': form})

@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'templates/dashboard.html', {'accounts': accounts, 'transactions': transactions})

@login_required
def deposit(request, account_id):
    account = Account.objects.get(id=account_id, user=request.user)
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        account.deposit(amount)
        Transaction.objects.create(user=request.user, account=account, transaction_type='deposit', amount=amount)
        return redirect('dashboard')
    return render(request, 'templates/deposit.html', {'account': account})

@login_required
def withdraw_view(request):
    accounts = Account.objects.filter(user=request.user)

    if request.method == 'POST':
        form = CashWithdrawalForm(request.POST)
        
        if form.is_valid():
            withdrawal_choice = form.cleaned_data['withdrawal_choice']
            amount = 0

            if withdrawal_choice == 'other':
                amount = form.cleaned_data['other_amount']
            else:
                amount = Decimal(withdrawal_choice)

            account_id = request.POST.get('account')
            account = accounts.filter(id=account_id).first()
            if not account:
                messages.error(request, "Invalid account selected.")
                return redirect('withdraw')

            if amount <= 0:
                messages.error(request, "Please enter a positive amount.")
            elif amount % 100 != 0:
                messages.error(request, "Please enter the amount in multiples of 100.")
            elif amount > account.balance:
                messages.error(request, "Insufficient balance in the account.")
            else:
                account.balance -= amount
                account.save()

                Transaction.objects.create(
                    user=request.user,
                    account=account,
                    transaction_type='withdrawal',
                    amount=amount
                )

                messages.success(request, f"Successfully withdrew {amount} from your account.")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid form data.")
    
    else:
        form = CashWithdrawalForm()

    return render(request, 'templates/withdraw.html', {'accounts': accounts, 'form': form})


@login_required
def balance_inquiry_view(request):
    accounts = Account.objects.filter(user=request.user)

    if not accounts.exists():
        messages.error(request, "No accounts found for this user.")
        return redirect('dashboard')

    return render(request, 'templates/balance_inquiry.html', {'accounts': accounts})

@login_required
def deposit_view(request, account_id=None):
    account = (
        Account.objects.filter(user=request.user).first()
        if account_id is None
        else Account.objects.filter(id=account_id, user=request.user).first()
    )

    if not account:
        messages.error(request, "No accounts found for this user.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            amount = request.POST.get('amount', '0')
            amount = Decimal(amount)

            if amount <= 0:
                raise ValueError("Please enter a positive amount.")
            if amount % 100 != 0:
                raise ValueError("Please enter the amount in multiples of 100.")

            account.balance += amount
            account.save()
            
            Transaction.objects.create(
                user=request.user,
                account=account,
                transaction_type='deposit',
                amount=amount
            )
            messages.success(request, f"Successfully deposited {amount} into your account.")
            return redirect('dashboard')

        except InvalidOperation:
            return render(request, 'templates/deposit.html', {
                'account': account,
                'error': "Invalid amount entered. Please enter a valid number."
            })
        except ValueError as e:
            return render(request, 'templates/deposit.html', {
                'account': account,
                'error': str(e)
            })

    return render(request, 'templates/deposit.html', {'account': account})

@login_required
def fund_transfer_view(request):
    if request.method == 'POST':
        sender_account = Account.objects.filter(user=request.user).first()

        if not sender_account:
            messages.error(request, "You do not have an account to transfer funds from.")
            return redirect('dashboard')

        try:
            recipient_account_number = request.POST.get('recipient_account_number')
            recipient_account_number = recipient_account_number.strip()
            amount = request.POST.get('amount', '0')
            amount = Decimal(amount)

            recipient_account = Account.objects.filter(account_number=recipient_account_number).first()

            if not recipient_account:
                raise ValueError("The recipient's account number does not exist.")
            
            if amount <= 0:
                raise ValueError("Please enter a positive amount.")
            if sender_account.balance < amount:
                raise ValueError("Insufficient balance.")

            sender_account.balance -= amount
            recipient_account.balance += amount
            sender_account.save()
            recipient_account.save()

            Transaction.objects.create(
                user=request.user,
                account=sender_account,
                transaction_type='transfer',
                amount=-amount,
                recipient_account=recipient_account,
            )

            Transaction.objects.create(
                user=recipient_account.user,
                account=recipient_account,
                transaction_type='transfer',
                amount=amount,
                recipient_account=recipient_account,
            )

            messages.success(request, f"Successfully transferred ${amount} to account {recipient_account_number}.")
            return redirect('dashboard')

        except InvalidOperation:
            messages.error(request, "Invalid amount entered. Please enter a valid number.")
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'templates/fund_transfer.html')


@login_required
def account_info_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)

    return render(request, 'templates/account_info.html', {'user': user, 'accounts': accounts})

@login_required
def user_update_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if password:
                request.user.set_password(password)
                form.save()
                request.user.save()
            else:
                form.save()

            messages.success(request, "Your information has been updated!")
            
            if password:
                messages.info(request, "Please log in again with your new password.")
                return redirect('login')
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'templates/user_update.html', {'form': form})



@login_required
def delete_user_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')

        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            request.user.is_active = False
            request.user.save()
            logout(request)

            messages.success(request, "Your account has been deleted successfully.")
            return redirect('login')  
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('delete_user')  

    return render(request, 'templates/delete_user.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return render(request, 'templates/logout.html')

@login_required
def recent_transactions_view(request):
    transactions = (
        Transaction.objects.filter(user=request.user)
        .select_related('account', 'recipient_account', 'user', 'recipient_account__user') 
        .order_by('-timestamp')
    )

    for transaction in transactions:
            transaction.sender_name = transaction.get_sender_name()
            transaction.receiver_name = transaction.get_receiver_name()

    return render(request, 'templates/recent_transactions.html', {'transactions': transactions})


