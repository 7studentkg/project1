from .models import Client, Document, DocumentFile, Payment, Refund, Mother, Father, Contact, Child
from rest_framework import serializers
import json

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id', 'file']

class DocumentSerializer(serializers.ModelSerializer):
    files = DocumentFileSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    delete_list = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Document
        fields = ['id', 'title', 'uploaded_at', 'files', 'uploaded_files', 'delete_list']

    def create(self, validated_data):
        files_data = validated_data.pop('uploaded_files')
        client_id = self.context['client_id']
        client = Client.objects.get(id=client_id)
        document = Document.objects.create(client=client, **validated_data)

        for file in files_data:
            doc_file = DocumentFile.objects.create(file=file)
            document.files.add(doc_file)
        return document

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['files'] = DocumentFileSerializer(instance.files.all(), many=True).data
        return representation

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['file'] = urllib.parse.unquote(representation['file'])
    #     return representation

    def update(self, instance, validated_data):
        files_data = validated_data.pop('uploaded_files', [])
        delete_list = validated_data.pop('delete_list', [])

        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # Добавление новых файлов
        for file in files_data:
            doc_file = DocumentFile.objects.create(file=file)
            instance.files.add(doc_file)

        # Удаление файлов из delete_list
        for file_id in delete_list:
            file_instance = DocumentFile.objects.filter(id=file_id).first()
            if file_instance:
                instance.files.remove(file_instance)
                file_instance.delete()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['files'] = DocumentFileSerializer(instance.files.all(), many=True).data
        return representation


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
        mother_data = self.initial_data.get('mother')
        father_data = self.initial_data.get('father')
        contact_data = self.initial_data.get('contact')
        children_data = self.initial_data.get('children', [])

        if mother_data:
            mother_data = json.loads(mother_data)
        if father_data:
            father_data = json.loads(father_data)
        if contact_data:
            contact_data = json.loads(contact_data)
        if children_data:
            children_data = json.loads(children_data)

        client = Client.objects.create(**validated_data)

        if mother_data:
            Mother.objects.create(client=client, **mother_data)
        if father_data:
            Father.objects.create(client=client, **father_data)
        if contact_data:
            Contact.objects.create(client=client, **contact_data)

        for child_data in children_data:
            Child.objects.create(client=client, **child_data)

        return client

    def update(self, instance, validated_data):
        mother_data = self.initial_data.get('mother', None)
        father_data = self.initial_data.get('father', None)
        contact_data = self.initial_data.get('contact', None)
        children_data = self.initial_data.get('children', [])

        if mother_data:
            mother_data = json.loads(mother_data)
        if father_data:
            father_data = json.loads(father_data)
        if contact_data:
            contact_data = json.loads(contact_data)
        if children_data:
            children_data = json.loads(children_data)

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

        instance.save()
        return instance



        # def create(self, validated_data):
    #     mother_data = validated_data.pop('mother', None)
    #     father_data = validated_data.pop('father', None)
    #     contact_data = validated_data.pop('contact', None)
    #     children_data = validated_data.pop('children', [])

    #     logger.debug(f"Raw mother data: {mother_data}")
    #     logger.debug(f"Raw father data: {father_data}")
    #     logger.debug(f"Raw contact data: {contact_data}")
    #     logger.debug(f"Raw children data: {children_data}")

    #     if isinstance(mother_data, str):
    #         mother_data = json.loads(mother_data)
    #     if isinstance(father_data, str):
    #         father_data = json.loads(father_data)
    #     if isinstance(contact_data, str):
    #         contact_data = json.loads(contact_data)
    #     if isinstance(children_data, str):
    #         children_data = json.loads(children_data)

    #     logger.debug(f"Processed mother data: {mother_data}")
    #     logger.debug(f"Processed father data: {father_data}")
    #     logger.debug(f"Processed contact data: {contact_data}")
    #     logger.debug(f"Processed children data: {children_data}")

    #     client = Client.objects.create(**validated_data)

    #     if mother_data:
    #         Mother.objects.create(client=client, **mother_data)
    #     if father_data:
    #         Father.objects.create(client=client, **father_data)
    #     if contact_data:
    #         Contact.objects.create(client=client, **contact_data)

    #     for child_data in children_data:
    #         Child.objects.create(client=client, **child_data)

    #     return client

    # def update(self, instance, validated_data):
    #     mother_data = validated_data.pop('mother', None)
    #     father_data = validated_data.pop('father', None)
    #     contact_data = validated_data.pop('contact', None)
    #     children_data = validated_data.pop('children', [])

    #     logger.debug(f"Raw mother data: {mother_data}")
    #     logger.debug(f"Raw father data: {father_data}")
    #     logger.debug(f"Raw contact data: {contact_data}")
    #     logger.debug(f"Raw children data: {children_data}")

    #     if isinstance(mother_data, str):
    #         mother_data = json.loads(mother_data)
    #     if isinstance(father_data, str):
    #         father_data = json.loads(father_data)
    #     if isinstance(contact_data, str):
    #         contact_data = json.loads(contact_data)
    #     if isinstance(children_data, str):
    #         children_data = json.loads(children_data)

    #     logger.debug(f"Processed mother data: {mother_data}")
    #     logger.debug(f"Processed father data: {father_data}")
    #     logger.debug(f"Processed contact data: {contact_data}")
    #     logger.debug(f"Processed children data: {children_data}")

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     if mother_data:
    #         Mother.objects.update_or_create(client=instance, defaults=mother_data)
    #     if father_data:
    #         Father.objects.update_or_create(client=instance, defaults=father_data)
    #     if contact_data:
    #         Contact.objects.update_or_create(client=instance, defaults=contact_data)

    #     existing_ids = [child.id for child in instance.children.all()]
    #     incoming_ids = [item['id'] for item in children_data if 'id' in item]

    #     for child_id in set(existing_ids) - set(incoming_ids):
    #         Child.objects.filter(id=child_id).delete()

    #     for child_data in children_data:
    #         child_id = child_data.get('id', None)
    #         if child_id:
    #             child = Child.objects.get(id=child_id, client=instance)
    #             for key, value in child_data.items():
    #                 setattr(child, key, value)
    #             child.save()
    #         else:
    #             Child.objects.create(client=instance, **child_data)

    #     instance.save()
    #     return instance
