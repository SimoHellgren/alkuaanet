from lib.models import Opus


class CRUDOpus:
    def get(self, table, tones: str) -> Opus | None:
        result = table.get_item(
            Key={
                "pk": "opus",
                "sk": tones,
            }
        )

        item = result.get("Item")

        if item:
            return Opus(**item)

        return None


opus = CRUDOpus()
