from app.settings import Settings


class TermsAndConditionsService:
    """Get the terms and conditions for the service."""

    def __init__(self):
        self.settings = Settings().get_settings()

    def get_privacy_policy(self) -> str:
        return f"""
<h1>{self.settings.ORG_NAME}</h1>

<h2>Privacy Policy</h2>

<h3>Effective Date: {self.settings.TNC_EFFECTIVE_DATE}</h3>

</br><b>1. Introduction</b></br>
This Privacy Policy explains how we collect, use, and protect your personal information when you use our service. By using our service, you agree to the terms outlined in this policy.

</br></br><b>2. Data Collection and Use</b></br>

We collect only the user's email address and name.

The primary purpose of data collection is to send daily updates about selected stock information to users' email addresses.

This data will not be used for any other purpose.

</br></br><b>3. Data Storage and Security</b></br>

User data is stored in an encrypted database to ensure security.

We do not share user data with any third parties.

</br></br><b>4. User Rights and Data Deletion</b></br>

Users can delete their data at any time by sending a DELETE request to an API endpoint we provide.

Data deletion requests are processed instantly.

Users can unsubscribe from emails by deleting their email data, which is the only personal data we store.

</br></br><b>5. Compliance with Data Privacy Laws</b>

</br>GDPR (EU Users): If you are an EU user, you have rights under GDPR, including the right to request access to your data, request deletion, and withdraw consent. Since our service does not process large-scale data, a Data Protection Officer (DPO) is not required.

</br></br>CCPA (California Users): If you are a California resident, you have the right to request and delete your data. Since we do not sell or share data, CCPA opt-out requirements do not apply.

</br></br>Singapore (PDPA Compliance): We comply with Singapore's PDPA, ensuring that personal data is collected and used with user consent.

</br></br>Email Compliance (CAN-SPAM, PECR): Our emails comply with anti-spam laws. Users can opt out at any time by deleting their email data.

</br></br><b>6. Changes to this Privacy Policy</b></br>
We reserve the right to update this policy. Updates will be made available via our GET API endpoint.

</br></br><b>7. Contact Information</b></br>
For any privacy-related inquiries, please contact <a href={self.settings.EMAIL_ADDRESS}>{self.settings.EMAIL_ADDRESS}</a>.
"""

    def get_terms_of_service(self) -> str:
        return f"""
<h1>{self.settings.ORG_NAME}</h1>

<h2>Terms of Service</h2>

<h3>Effective Date: {self.settings.TNC_EFFECTIVE_DATE}</h3>

</br><b>1. Introduction</b>
</br>These Terms of Service govern your use of our service. By using the service, you agree to these terms.

</br></br><b>2. User Responsibilities</b>

</br>There are no user restrictions; users are not required to provide accurate information.

</br>Users may supply their email address to receive stock updates.

</br></br><b>3. Account Management</b>

</br>Users can create and delete their accounts at any time.

</br>There are no account suspensions or terminations, as users do not have write access beyond supplying their email.

</br></br><b>4. Service Availability and Limitations</b>

</br>This service is provided as a personal project.

</br>No support or guarantees of availability are offered.

</br></br><b>5. Liability Disclaimer</b>

</br>We accept no liability for service interruptions, errors, or damages resulting from using the service.

</br></br><b>6. Changes to the Terms</b>

</br>Updates to these terms will be published via our publicly accessible GET API endpoint.

</br></br><b>7. Contact Information</b>
</br>For any inquiries regarding these terms, please contact <a href={self.settings.EMAIL_ADDRESS}>{self.settings.EMAIL_ADDRESS}</a>.
"""
