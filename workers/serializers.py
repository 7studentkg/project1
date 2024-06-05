from .models import Client, Document, DocumentFile, Payment, Refund, Mother, Father, Contact, Child
from rest_framework import serializers


class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['pk', 'file']

class DocumentSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'uploaded_at', 'files']

    def get_files(self, obj):
        documents = Document.objects.filter(client=obj.client, title=obj.title)
        return DocumentFileSerializer(documents, many=True).data

class MultipleDocumentsSerializer(serializers.Serializer):
    documents = serializers.ListField(
        child=serializers.FileField()
    )

    def create(self, validated_data):
        client_id = self.context['client_id']
        client = Client.objects.get(id=client_id)
        documents = validated_data.pop('documents')
        title = self.context['title']
        uploaded_at = self.context['uploaded_at']

        # Create the main document group
        doc_group = Document.objects.create(client=client, title=title, uploaded_at=uploaded_at, is_group=True)

        # Create nested documents for each file
        for document_file in documents:
            Document.objects.create(client=client, file=document_file, title=title, is_group=False)

        return doc_group


# class DocumentFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DocumentFile
#         fields = ['id', 'file']


# class DocumentSerializer(serializers.ModelSerializer):
#     files = DocumentFileSerializer(many=True, read_only=True)

#     class Meta:
#         model = Document
#         fields = ['id', 'title', 'uploaded_at', 'files']

#     def create(self, validated_data):
#         document = Document.objects.create(**validated_data)
#         return document



class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'title', 'uploaded_at']

    def create(self, validated_data):
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        validated_data['client'] = client
        return super().create(validated_data)


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'amount', 'title', 'uploaded_at']

    def create(self, validated_data):
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        validated_data['client'] = client
        return super().create(validated_data)



class MotherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mother
        fields = ['id', 'name', 'phone', 'birthDate']


class FatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Father
        fields = ['id', 'name', 'phone', 'birthDate']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'birthDate']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'name', 'birthDate']


class ClientSerializer(serializers.ModelSerializer):
    # country = serializers.PrimaryKeyRelatedField(
    #     queryset=Country.objects.all(),
    #     many=True
    # )
    # status = serializers.PrimaryKeyRelatedField(
    #     queryset=Status.objects.all(),
    #     read_only=False
    # )

    mother = MotherSerializer(required=False)
    father = FatherSerializer(required=False)
    contact = ContactSerializer(required=False)
    children = ChildSerializer(many=True, required=False)


    class Meta:
        model = Client
        fields = [
            'id', 'image', 'birthLastName', 'currentLastName', 'firstName', 'birthDate', 'birthPlace', 'residence',
            'passportNumber', 'passportIssueDate', 'passportExpirationDate', 'passportIssuingAuthority',
            'email', 'password', 'height', 'weight', 'englishLevel', 'familyStatus', 'country',
            'status', 'mother', 'father', 'contact', 'children',
            'uploaded_at', 'last_modified'
        ]

    def create(self, validated_data):
        mother_data = validated_data.pop('mother', None)
        father_data = validated_data.pop('father', None)
        contact_data = validated_data.pop('contact', None)
        children_data = validated_data.pop('children', [])
        # document_files = self.context['request'].FILES

        client = Client.objects.create(**validated_data)
        if mother_data is not None:
            Mother.objects.create(client=client, **mother_data)
        if father_data is not None:
            Father.objects.create(client=client, **father_data)
        if contact_data is not None:
            Contact.objects.create(client=client, **contact_data)

        for child_data in children_data:
            Child.objects.create(client=client, **child_data)


        # for key, file in document_files.items():
        #     title = validated_data.get('title', '')
        #     Document.objects.create(client=client, file=file, title=title)

        return client

    def update(self, instance, validated_data):
        mother_data = validated_data.pop('mother', None)
        father_data = validated_data.pop('father', None)
        contact_data = validated_data.pop('contact', None)
        children_data = validated_data.pop('children', [])
        # document_files = self.context['request'].FILES

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if mother_data:
            Mother.objects.update_or_create(client=instance, defaults=mother_data)
        if father_data:
            Father.objects.update_or_create(client=instance, defaults=father_data)
        if contact_data:
            Contact.objects.update_or_create(client=instance, defaults=contact_data)

        existing_ids = [child.id for child in instance.children.all()]
        incoming_ids = [item['id'] for item in children_data if 'id' in item]

        for child_id in set(existing_ids) - set(incoming_ids):
            Child.objects.filter(id=child_id).delete()

        for child_data in children_data:
            child_id = child_data.get('id', None)
            if child_id:
                child = Child.objects.get(id=child_id, client=instance)
                for key, value in child_data.items():
                    setattr(child, key, value)
                child.save()
            else:
                Child.objects.create(client=instance, **child_data)

        # for key, file in document_files.items():
        #     title = validated_data.get('title', '')
        #     Document.objects.create(client=instance, file=file, title=title)

        instance.save()
        return instance
