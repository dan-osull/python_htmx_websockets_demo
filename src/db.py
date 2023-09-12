from tortoise import fields
from tortoise.models import Model


class Link(Model):
    id = fields.UUIDField(pk=True)
    added = fields.DatetimeField(auto_now_add=True)
    url = fields.TextField()
    title = fields.TextField(default=None, null=True)
    user_emoji = fields.TextField(default="🐍")

    @property
    def div_id(self) -> str:
        return "node_" + "".join(char for char in str(self.id) if char.isalnum())

    @property
    def added_date(self) -> str:
        return self.added.strftime("%-d %b %Y")

    @property
    def added_time(self) -> str:
        return self.added.strftime("%H:%M")

    @property
    def display_name(self) -> str:
        name = str(self.url)
        if self.title is not None:
            name = self.title
        if len(name) > 100:
            name = name[:100] + "..."
        return name
