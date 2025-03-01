"""
Provides functionality to seed the database with demo data for development and testing purposes.
Creates sample organizations, users, attorneys, rates, negotiations, and other entities for the Justice Bid Rate Negotiation System.
"""

import datetime  # standard library
import random  # standard library
import uuid  # standard library
import json  # standard library

from faker import Faker  # ^15.0.0

from ..session import get_db  # Database session management
from ..models import user as user_model  # Database models for entities
from ..models import organization as organization_model  # Database models for entities
from ..models import attorney as attorney_model  # Database models for entities
from ..models import staff_class as staff_class_model  # Database models for entities
from ..models import peer_group as peer_group_model  # Database models for entities
from ..models import rate as rate_model  # Database models for entities
from ..models import negotiation as negotiation_model  # Database models for entities
from ..models import message as message_model  # Database models for entities
from ..models import ocg as ocg_model  # Database models for entities
from ..models import billing as billing_model  # Database models for entities
from ...utils.security import get_password_hash  # Security utilities for password hashing
from ...utils.constants import OrganizationType, RateStatus, RateType, NegotiationStatus, UserRole  # System constants and enumerations

faker = Faker()  # Instance of Faker for generating realistic data

def seed_demo_data():
    """Main function to seed all demo data into the database"""
    db = get_db()  # Get database session

    law_firms = create_law_firms(db)  # Create law firm organizations
    clients = create_clients(db)  # Create client organizations
    users_by_org = create_users(db, law_firms, clients)  # Create users for organizations
    attorneys_by_firm = create_attorneys(db, law_firms)  # Create attorneys for law firms
    staff_classes_by_client = create_staff_classes(db, clients)  # Create staff classes
    peer_groups = create_peer_groups(db, law_firms, clients)  # Create peer groups
    rates_by_relationship = create_rates(db, attorneys_by_firm, clients, law_firms, staff_classes_by_client)  # Create rates
    negotiations = create_negotiations(db, law_firms, clients, rates_by_relationship)  # Create negotiations
    message_threads = create_messages(db, negotiations, users_by_org)  # Create messages
    ocgs_by_client = create_ocgs(db, clients)  # Create OCGs
    billing_history = create_billing_history(db, attorneys_by_firm, clients)  # Create billing history data

    db.commit()  # Commit session to save all data

def create_law_firms(session):
    """Creates sample law firm organizations"""
    law_firm_names = ["Acme Law Firm", "Beta Legal", "Gamma Attorneys"]  # Define law firm names and domains
    law_firm_domains = ["acmelaw.com", "betalegal.net", "gammaattorneys.org"]

    law_firms = []
    for name, domain in zip(law_firm_names, law_firm_domains):  # Create organization objects with type 'LawFirm'
        org = organization_model.Organization(name=name, type=OrganizationType.LAW_FIRM, domain=domain)
        org.settings = {"billing_system": "LexisNexis Time Matters"}  # Add settings for each law firm
        session.add(org)
        law_firms.append(org)

    return law_firms  # Return list of created organizations

def create_clients(session):
    """Creates sample client organizations"""
    client_names = ["Acme Corporation", "Beta Industries", "Gamma Corp"]  # Define client company names and domains
    client_domains = ["acmecorp.com", "betaindustries.net", "gammacorp.org"]

    clients = []
    for name, domain in zip(client_names, client_domains):  # Create organization objects with type 'Client'
        org = organization_model.Organization(name=name, type=OrganizationType.CLIENT, domain=domain)
        org.settings = {  # Add rate rules and settings for each client
            "rate_rules": {
                "max_increase_percent": 5,
                "notice_period": 90,
                "rate_freeze_period": 180
            },
            "ebilling_system": "Onit"
        }
        session.add(org)
        clients.append(org)

    return clients  # Return list of created organizations

def create_users(session, law_firms, clients):
    """Creates sample users for both law firms and clients"""
    users_by_org = {}

    for org in law_firms + clients:
        users = []
        # Create admin, regular users for each law firm
        if org.type == OrganizationType.LAW_FIRM:
            admin_user = user_model.User(
                email=f"admin@{org.domain}",
                name=f"Admin User ({org.name})",
                password="password123",
                organization_id=org.id,
                role=UserRole.ORGANIZATION_ADMINISTRATOR
            )
            session.add(admin_user)
            users.append(admin_user)

            regular_user = user_model.User(
                email=f"user@{org.domain}",
                name=f"Regular User ({org.name})",
                password="password123",
                organization_id=org.id,
                role=UserRole.STANDARD_USER
            )
            session.add(regular_user)
            users.append(regular_user)

        # Create admin, approver, and regular users for each client
        elif org.type == OrganizationType.CLIENT:
            admin_user = user_model.User(
                email=f"admin@{org.domain}",
                name=f"Admin User ({org.name})",
                password="password123",
                organization_id=org.id,
                role=UserRole.ORGANIZATION_ADMINISTRATOR
            )
            session.add(admin_user)
            users.append(admin_user)

            approver_user = user_model.User(
                email=f"approver@{org.domain}",
                name=f"Approver User ({org.name})",
                password="password123",
                organization_id=org.id,
                role=UserRole.APPROVER
            )
            session.add(approver_user)
            users.append(approver_user)

            regular_user = user_model.User(
                email=f"user@{org.domain}",
                name=f"Regular User ({org.name})",
                password="password123",
                organization_id=org.id,
                role=UserRole.STANDARD_USER
            )
            session.add(regular_user)
            users.append(regular_user)

        users_by_org[org.id] = users  # Return dictionary of users organized by organization

    return users_by_org

def create_attorneys(session, law_firms):
    """Creates sample attorneys for law firms"""
    attorneys_by_firm = {}

    for org in law_firms:  # For each law firm, create partner, senior associate, and junior attorneys
        attorneys = []
        for i in range(3):
            # Set experience levels, bar dates, graduation dates
            years_of_experience = random.randint(5, 20)
            bar_date = faker.date_between(start_date="-20y", end_date="-5y").date()
            graduation_date = faker.date_between(start_date="-24y", end_date="-7y").date()

            attorney = attorney_model.Attorney(
                organization_id=org.id,
                name=faker.name(),
                bar_date=bar_date,
                graduation_date=graduation_date,
            )
            # Generate unique timekeeper IDs for each client integration
            attorney.timekeeper_ids = {
                "client1": faker.bothify(text='TK-????##'),
                "client2": faker.bothify(text='ATY-####')
            }
            attorneys.append(attorney)
            session.add(attorney)

        attorneys_by_firm[org.id] = attorneys  # Return dictionary of attorneys organized by law firm

    return attorneys_by_firm

def create_staff_classes(session, clients):
    """Creates standard staff classes for client organizations"""
    staff_classes_by_client = {}

    for org in clients:  # For each client, create standard staff classes (Partner, Senior Associate, etc.)
        staff_classes = []
        partner_class = staff_class_model.StaffClass(
            organization_id=org.id,
            name="Partner",
            experience_type="years_in_role",
            min_experience=10
        )
        session.add(partner_class)
        staff_classes.append(partner_class)

        associate_class = staff_class_model.StaffClass(
            organization_id=org.id,
            name="Associate",
            experience_type="years_in_role",
            min_experience=3,
            max_experience=7
        )
        session.add(associate_class)
        staff_classes.append(associate_class)

        paralegal_class = staff_class_model.StaffClass(
            organization_id=org.id,
            name="Paralegal",
            experience_type="years_in_role",
            min_experience=1
        )
        session.add(paralegal_class)
        staff_classes.append(paralegal_class)

        staff_classes_by_client[org.id] = staff_classes  # Return dictionary of staff classes organized by client

    return staff_classes_by_client

def create_peer_groups(session, law_firms, clients):
    """Creates peer groups for comparing law firms and clients"""
    peer_groups = {}

    for org in law_firms:  # Create AmLaw 100 peer group for law firms
        amlaw_group = peer_group_model.PeerGroup(
            organization_id=org.id,
            name="AmLaw 100",
            criteria={"ranking": "top 100"}
        )
        session.add(amlaw_group)
        peer_groups[org.id] = amlaw_group

    for org in clients:  # Create Fortune 500 peer group for clients
        fortune_group = peer_group_model.PeerGroup(
            organization_id=org.id,
            name="Fortune 500",
            criteria={"industry": "technology"}
        )
        session.add(fortune_group)
        peer_groups[org.id] = fortune_group

    return peer_groups

def create_rates(session, attorneys_by_firm, clients, law_firms, staff_classes_by_client):
    """Creates historical and current rate data for attorneys"""
    rates_by_relationship = {}

    for firm in law_firms:  # For each attorney-client relationship, create rate history (3+ years)
        for client in clients:
            for attorney in attorneys_by_firm[firm.id]:
                # Set appropriate rates based on attorney seniority and client tier
                base_rate = random.randint(300, 800)
                if client.name == "Acme Corporation":
                    base_rate *= 1.1  # Charge Acme more
                elif attorney.name.startswith("Senior"):
                    base_rate *= 1.2

                # Create standard, approved, and proposed rates
                rate = rate_model.Rate(
                    attorney_id=attorney.id,
                    client_id=client.id,
                    firm_id=firm.id,
                    office_id=firm.offices[0].id if firm.offices else None,
                    staff_class_id=attorney.staff_class_id,
                    amount=base_rate,
                    currency="USD",
                    effective_date=datetime.date(2023, 1, 1),
                    expiration_date=None,
                    type=RateType.STANDARD,
                    status=RateStatus.APPROVED
                )
                session.add(rate)
                rates_by_relationship[(attorney.id, client.id)] = rate  # Associate attorneys with appropriate staff classes

    return rates_by_relationship

def create_negotiations(session, law_firms, clients, rates_by_relationship):
    """Creates sample rate negotiations between firms and clients"""
    negotiations = []

    for firm in law_firms:  # Create negotiations in various states (Requested, InProgress, Completed)
        for client in clients:
            negotiation = negotiation_model.Negotiation(
                client_id=client.id,
                firm_id=firm.id,
                status=NegotiationStatus.IN_PROGRESS,
                request_date=datetime.date(2023, 9, 15),
                submission_deadline=datetime.date(2023, 10, 31)
            )
            session.add(negotiation)
            negotiations.append(negotiation)

            # Associate appropriate rates with each negotiation
            for attorney in firm.attorneys:
                if (attorney.id, client.id) in rates_by_relationship:
                    negotiation.rates.append(rates_by_relationship[(attorney.id, client.id)])

    return negotiations

def create_messages(session, negotiations, users_by_org):
    """Creates sample messages for negotiations"""
    message_threads = {}

    for negotiation in negotiations:  # For each negotiation, create message thread with multiple messages
        messages = []
        # Set appropriate sender and recipient information
        if negotiation.firm_id in users_by_org and negotiation.client_id in users_by_org:
            firm_user = users_by_org[negotiation.firm_id][0]
            client_user = users_by_org[negotiation.client_id][0]

            # Add realistic message content related to rate negotiations
            message1 = message_model.Message(
                thread_id=negotiation.id,
                sender_id=firm_user.id,
                recipient_ids=[client_user.id],
                content=generate_sample_message("initial_request", firm.name, client.name)
            )
            session.add(message1)
            messages.append(message1)

            message2 = message_model.Message(
                thread_id=negotiation.id,
                sender_id=client_user.id,
                recipient_ids=[firm_user.id],
                content=generate_sample_message("counter_offer", firm.name, client.name),
                parent_id=message1.id
            )
            session.add(message2)
            messages.append(message2)

        message_threads[negotiation.id] = messages  # Return dictionary of message threads

    return message_threads

def create_ocgs(session, clients):
    """Creates sample Outside Counsel Guidelines for clients"""
    ocgs_by_client = {}

    for client in clients:  # For each client, create OCG document with sections
        ocg = ocg_model.OCG(
            client_id=client.id,
            name=f"Standard OCG for {client.name}",
            version=1,
            total_points=10,
            default_firm_point_budget=5
        )
        session.add(ocg)
        ocgs_by_client[client.id] = ocg

    return ocgs_by_client

def create_billing_history(session, attorneys_by_firm, clients):
    """Creates sample billing history data for analytics"""
    billing_history = {}

    for firm_id, attorneys in attorneys_by_firm.items():  # Generate 3+ years of historical billing data
        for client in clients:
            for attorney in attorneys:
                # Vary billing patterns by attorney seniority
                hourly_rate = random.randint(200, 700)
                if attorney.name.startswith("Senior"):
                    hourly_rate *= 1.2

                # Include mix of AFA and hourly billing based on client preferences
                for month in range(1, 13):
                    billing_date = datetime.date(2022, month, 15)
                    hours = random.randint(10, 40)
                    fees = hourly_rate * hours
                    is_afa = random.random() < 0.2  # 20% chance of AFA

                    billing_record = billing_model.BillingHistory(
                        attorney_id=attorney.id,
                        client_id=client.id,
                        hours=hours,
                        fees=fees,
                        billing_date=billing_date,
                        is_afa=is_afa
                    )
                    session.add(billing_record)

    return billing_history

def generate_rate_history(base_rate, years, avg_increase_pct):
    """Helper function to generate historical rate progression"""
    rates = []
    current_rate = base_rate

    for year_offset in range(years):  # Work backwards applying inverse of average increase
        year = datetime.datetime.now().year - year_offset
        increase = 1 + (avg_increase_pct + random.uniform(-0.01, 0.01))
        current_rate /= increase
        rates.append({"year": year, "rate": round(current_rate, 2)})

    return rates

def generate_sample_message(message_type, firm_name, client_name):
    """Helper function to generate realistic negotiation messages"""
    if message_type == "initial_request":  # Select appropriate message template based on message type
        return f"Dear {client_name},\n\n{firm_name} is pleased to submit our rate proposals for 2024. We value our partnership and look forward to a successful negotiation.\n\nSincerely,\n{faker.name()}"
    elif message_type == "counter_offer":
        return f"Dear {firm_name},\n\nThank you for your submission. We have reviewed your proposals and are providing counter-offers for certain attorneys based on our budget guidelines.\n\nBest regards,\n{faker.name()}"
    else:
        return "This is a sample message for demonstration purposes."