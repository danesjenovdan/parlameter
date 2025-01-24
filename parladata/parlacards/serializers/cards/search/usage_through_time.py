from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.solr import parse_search_query_params, solr_select


class BaseUsageThroughTimeCardSerializer(CardSerializer):
    def get_results(self, mandate, document_type, fl):
        solr_params = parse_search_query_params(self.context.get("GET", {}), facet=True)
        solr_params["mandate"] = mandate.id
        solr_response = solr_select(
            **solr_params, per_page=0, document_type=document_type, fl=fl
        )

        if (
            not solr_response.get("facet_counts", {})
            .get("facet_ranges", {})
            .get("start_time", {})
            .get("counts", [])
        ):
            return None

        facet_counts = solr_response["facet_counts"]["facet_ranges"]["start_time"][
            "counts"
        ]
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {"timestamp": timestamp, "value": value}
            for (timestamp, value) in facet_counts_tuples
        ]

        return objects

    def get_mandate(self, mandate):
        serializer = MandateSerializer(mandate, context=self.context)

        return serializer.data


class MandateUsageThroughTimeInSpeechesCardSerializer(
    BaseUsageThroughTimeCardSerializer
):
    def get_results(self, mandate):
        return super().get_results(mandate, document_type="speech", fl="speech_id")


class MandateUsageThroughTimeInAgendaItemsCardSerializer(
    BaseUsageThroughTimeCardSerializer
):
    def get_results(self, mandate):
        return super().get_results(
            mandate, document_type="agenda_item", fl="agenda_item_id"
        )
