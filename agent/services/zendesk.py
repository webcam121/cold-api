from django.conf import settings
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User, Comment

creds = {'email': settings.ZENDESK_EMAIL, 'token': settings.ZENDESK_TOKEN, 'subdomain': settings.ZENDESK_SUBDOMAIN}


class ZendeskAPI:
    group_id = 23553594402715

    @classmethod
    def send_notification(
            cls,
            first_name,
            last_name,
            email,
            subject,
            status,
            tags,
            assignee_id=None,
            html_body=None,
            sms=True,
            body=None,
            agent_email=None,
            **kwargs,
    ):
        # if settings.ENVIRONMENT != 'production':
        #     return True

        if not last_name:
            last_name = ""

        if agent_email:
            creds = {
                'email': agent_email,
                'token': settings.ZENDESK_TOKEN,
                'subdomain': settings.ZENDESK_SUBDOMAIN,
            }

            zenpy_client = Zenpy(**creds)
        else:
            creds = {
                'email': settings.ZENDESK_EMAIL,
                'token': settings.ZENDESK_TOKEN,
                'subdomain': settings.ZENDESK_SUBDOMAIN,
            }

            zenpy_client = Zenpy(**creds)

        if sms and not body:
            raise ValueError('Provide body param if sms is True')

        ticket_params = {
            **({'assignee_id': assignee_id} if assignee_id else {}),
        }
        try:
            if sms:
                zenpy_client.tickets.create(
                    Ticket(
                        **ticket_params,
                        subject=subject,
                        group_id=cls.group_id,
                        requester=User(name=f'{first_name} {last_name}', email=email),
                        **({'comment': Comment(body=body)} if body else {'comment': Comment(html_body=html_body)}),
                        tags=['proactivetext'] + tags,
                        status=status,
                        **kwargs,
                    )
                )

            email_resp = zenpy_client.tickets.create(
                Ticket(
                    **ticket_params,
                    subject=subject,
                    group_id=cls.group_id,
                    requester=User(name=f'{first_name} {last_name}', email=email) if first_name else User(name=email.split('@')[0], email=email),
                    **({'comment': Comment(html_body=html_body)} if html_body else {'comment': Comment(body=body)}),
                    tags=tags,
                    status=status,
                    **kwargs,
                )
            )
            return [email_resp.ticket.id]
        except Exception as e:
            # sentry_sdk.capture_exception(e)
            print(e)
