import logging
from abc import ABC, abstractmethod
from django.conf import settings
import ghasedak_sms

logger = logging.getLogger(__name__)


class SMSProvider(ABC):
    @abstractmethod
    def send_otp(self, phone_number: str, code: str) -> bool:
        pass


class ConsoleProvider(SMSProvider):
    """Development provider that just prints the OTP to console"""

    def send_otp(self, phone_number: str, code: str) -> bool:
        message = f"\n-----------------\nSMS to {phone_number}\nYour verification code: {code}\n-----------------\n"
        print(message)
        logger.info(message)
        return True


class GhasedakProvider(SMSProvider):
    """Ghasedak SMS Provider - https://ghasedak.me/"""

    def send_otp(self, phone_number: str, code: str) -> bool:
        try:
            sms_api = ghasedak_sms.Ghasedak(settings.SMS_API_KEY)

            phone_number = str(phone_number)
            if phone_number.startswith('+98'):
                phone_number = '0' + phone_number[3:]

            # response = sms_api.send_otp_sms(receptor=phone_number, message='Your OTP message')
            # Send OTP using the verification template
            response = sms_api.send_otp_sms(ghasedak_sms.SendOtpInput(
                send_date=None,
                receptors=[
                    ghasedak_sms.SendOtpReceptorDto(
                        mobile=phone_number,
                    )
                ],
                template_name=settings.SMS_TEMPLATE_NAME,
                inputs=[
                    ghasedak_sms.SendOtpInput.OtpInput(param='Code', value=code),
                ],
                udh=False
            ))

            if response.get('isSuccess', False):
                logger.info(f"OTP sent successfully to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send OTP via Ghasedak: {response}")
                return False

        except Exception as e:
            logger.error(f"Error sending OTP via Ghasedak: {str(e)}")
            return False


class KavenegarProvider(SMSProvider):
    """Kavenegar SMS Provider"""

    def send_otp(self, phone_number: str, code: str) -> bool:
        try:
            from kavenegar import KavenegarAPI
            api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
            params = {
                'receptor': str(phone_number),
                'message': f'کد تایید شما در فیلم‌گزین: {code}',
            }
            api.sms_send(params)
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS via Kavenegar: {e}")
            return False


def get_sms_provider() -> SMSProvider:
    provider_name = settings.SMS_PROVIDER
    providers = {
        'console': ConsoleProvider,
        'ghasedak': GhasedakProvider,
        'kavenegar': KavenegarProvider,
    }
    provider_class = providers.get(provider_name.lower(), ConsoleProvider)
    return provider_class()
