from datetime import datetime


class TimelineGenerator:

    @staticmethod
    def build(metadata):

        timeline = []

        for item in metadata:

            timeline.append({
                "time": item["created"],
                "event": "Created",
                "file": item["name"]
            })

            timeline.append({
                "time": item["modified"],
                "event": "Modified",
                "file": item["name"]
            })

            timeline.append({
                "time": item["accessed"],
                "event": "Accessed",
                "file": item["name"]
            })

        timeline.sort(
            key=lambda x: datetime.fromisoformat(x["time"]) #to match with iso format
        )


        return timeline