import channels.layers
import json
from interviews.models import InterviewData, Interviewer
from interviews.serializers import GetIntervieweeSlotSerializer, GetInterviewerSlotSerializer
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.db.models import signals
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Q
from django.db.models import Count

class InterviewDataConsumer(JsonWebsocketConsumer):

    def fetch_data(self):
        if hasattr(self.user, 'interviewer'):
            interview_slots = InterviewData.objects.annotate(current_interviewers=Count('interviewers')) \
                                                   .filter(Q(current_interviewers__lt=F('max_interviewers')) | Q(interviewers__user=self.user))
            interview_slots = interview_slots.filter(digital_impact=self.user.interviewer.digital_impact)
            interviewer_slot_serializer = GetInterviewerSlotSerializer(interview_slots, many=True)
            return interviewer_slot_serializer.data
        elif hasattr(self.user, 'interviewee'):
            interview_slots = InterviewData.objects.annotate(current_interviewees=Count('interviewees'), current_interviewers=Count('interviewers')) \
                                                   .filter(current_interviewees__lt=F('max_interviewees')) \
                                                   .filter(current_interviewers__exact=F('max_interviewers'))
            interview_slots = interview_slots.filter(digital_impact=self.user.interviewee.digital_impact)
            interviewee_slot_serializer = GetIntervieweeSlotSerializer(interview_slots, many=True)
            return interviewee_slot_serializer.data
        else:
            response = {'errors': "user isn't an interviewer or interviewee"}
            return response

    def connect(self):
        self.user = self.scope["user"]
        async_to_sync(self.channel_layer.group_add)('interview_data_request_group', self.channel_name)
        self.accept()
        self.send_json(self.fetch_data())

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)('interview_data_request_group', self.channel_name)
        self.close()

    def receive_json(self, content, **kwargs):
        pass

    def broadcast_save(self, event):
        self.send_json(self.fetch_data())

    @staticmethod
    @receiver(signals.post_save, sender=InterviewData)
    def order_offer_observer(sender, instance, **kwargs):
        layer = channels.layers.get_channel_layer()
        async_to_sync(layer.group_send)('interview_data_request_group', {
            'type': 'broadcast_save',
        })