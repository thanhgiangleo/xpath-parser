from ..models import Domain


class UserRepository:

    @staticmethod
    def create(username: str, avatar_url: str) -> dict:
        """ Create user """
        result: dict = {}
        try:
            user = Domain(username=username, avatar_url=avatar_url)
            user.save()
            result = {
                'username': user.username,
                'avatar_url': user.avatar_url,
                'date_created': str(user.date_created),
            }
        except Exception:
            Domain.rollback()
            raise Exception('user already exists')

        return result

    @staticmethod
    def get(username: str) -> dict:
        """ Query a user by username """
        user: dict = {}
        user = Domain.query.filter_by(username=username).first_or_404()
        user = {
            'username': user.username,
            'date_created': str(user.date_created),
        }
        return user