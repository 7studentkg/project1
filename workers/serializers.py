from .models import ( Client, Document, DocumentFile, Payment, Refund, Mother,
                      Father, Contact, Child, Partner, PartnerClass, PaymentFile, RefundFile)
from rest_framework import serializers
import json
import mimetypes



class DocumentFileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFile
        fields = ('id', 'file', 'file_name')

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1]



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
        fields = ['id', 'title', 'uploaded_at', 'last_modified', 'files', 'uploaded_files', 'delete_list']

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



class PaymentFileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentFile
        fields = ('id', 'file', 'file_name')

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1]

class RefundFileSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = RefundFile
        fields = ('id', 'file', 'file_name')

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1]



class PaymentSerializer(serializers.ModelSerializer):
    files = PaymentFileSerializer(many=True, read_only=True)
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
        model = Payment
        fields = ['id', 'amount', 'title', 'files', 'uploaded_at', 'last_modified', 'uploaded_files', 'delete_list']

    def create(self, validated_data):
        files_data = validated_data.pop('uploaded_files', [])
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        payment = Payment.objects.create(client=client, **validated_data)

        if len(files_data) > 3:
            raise serializers.ValidationError("You can only upload up to 3 files.")

        for file in files_data:
            payment_file = PaymentFile.objects.create(file=file)
            payment.files.add(payment_file)
        return payment

    def update(self, instance, validated_data):
        files_data = validated_data.pop('uploaded_files', [])
        delete_list = validated_data.pop('delete_list', [])

        instance.amount = validated_data.get('amount', instance.amount)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if len(instance.files.all()) + len(files_data) > 3:
            raise serializers.ValidationError("You can only upload up to 3 files.")

        for file in files_data:
            payment_file = PaymentFile.objects.create(file=file)
            instance.files.add(payment_file)

        for file_id in delete_list:
            file_instance = PaymentFile.objects.filter(id=file_id).first()
            if file_instance:
                instance.files.remove(file_instance)
                file_instance.delete()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['files'] = PaymentFileSerializer(instance.files.all(), many=True).data
        return representation

class RefundSerializer(serializers.ModelSerializer):
    files = RefundFileSerializer(many=True, read_only=True)
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
        model = Refund
        fields = ['id', 'amount', 'title', 'files', 'uploaded_at', 'last_modified', 'uploaded_files', 'delete_list']

    def create(self, validated_data):
        files_data = validated_data.pop('uploaded_files', [])
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        refund = Refund.objects.create(client=client, **validated_data)

        if len(files_data) > 3:
            raise serializers.ValidationError("You can only upload up to 3 files.")

        for file in files_data:
            refund_file = RefundFile.objects.create(file=file)
            refund.files.add(refund_file)

        return refund

    def update(self, instance, validated_data):
        files_data = validated_data.pop('uploaded_files', [])
        delete_list = validated_data.pop('delete_list', [])

        instance.amount = validated_data.get('amount', instance.amount)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if len(instance.files.all()) + len(files_data) > 3:
            raise serializers.ValidationError("You can only upload up to 3 files.")

        for file in files_data:
            refund_file = RefundFile.objects.create(file=file)
            instance.files.add(refund_file)

        for file_id in delete_list:
            file_instance = RefundFile.objects.filter(id=file_id).first()
            if file_instance:
                instance.files.remove(file_instance)
                file_instance.delete()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['files'] = RefundFileSerializer(instance.files.all(), many=True).data
        return representation




# class PaymentSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Payment
#         fields = ['id', 'amount', 'title', 'file_check', 'uploaded_at', 'last_modified']

#     def create(self, validated_data):
#         client_id = self.context['view'].kwargs['client_id']
#         client = Client.objects.get(id=client_id)
#         validated_data['client'] = client
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         instance.amount = validated_data.get('amount', instance.amount)
#         instance.title = validated_data.get('title', instance.title)
#         instance.file_check = validated_data.get('file_check', instance.file_check)
#         instance.save()
#         return instance

# class RefundSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Refund
#         fields = ['id', 'amount', 'title', 'file_check', 'uploaded_at', 'last_modified']

#     def create(self, validated_data):
#         client_id = self.context['view'].kwargs['client_id']
#         client = Client.objects.get(id=client_id)
#         validated_data['client'] = client
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         instance.amount = validated_data.get('amount', instance.amount)
#         instance.title = validated_data.get('title', instance.title)
#         instance.file_check = validated_data.get('file_check', instance.file_check)
#         instance.save()
#         return instance

# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         fields = ['id', 'amount', 'title', 'file_check', 'uploaded_at', 'last_modified']

#     def create(self, validated_data):
#         client_id = self.context.get('client_id')
#         client = Client.objects.get(id=client_id)
#         validated_data['client'] = client
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         instance.amount = validated_data.get('amount', instance.amount)
#         instance.title = validated_data.get('title', instance.title)
#         instance.file_check = validated_data.get('file_check', instance.file_check)
#         instance.save()
#         return instance

# class RefundSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Refund
#         fields = ['id', 'amount', 'title', 'file_check', 'uploaded_at', 'last_modified']

#     def create(self, validated_data):
#         client_id = self.context.get('client_id')
#         client = Client.objects.get(id=client_id)
#         validated_data['client'] = client
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         instance.amount = validated_data.get('amount', instance.amount)
#         instance.title = validated_data.get('title', instance.title)
#         instance.file_check = validated_data.get('file_check', instance.file_check)
#         instance.save()
#         return instance

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


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'currentLastName', 'firstName', 'birthDate', 'country', 'status']



class PartnerClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerClass
        fields = ['id', 'name']

class PartnerSerializer(serializers.ModelSerializer):
    name_partner = serializers.SlugRelatedField(
        queryset=PartnerClass.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = Partner
        fields = ['id', 'name_partner', 'text']




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
    partners = PartnerSerializer(many=True, required=False, read_only=True)
    related_clients = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), many=True, required=False)



    class Meta:
        model = Client
        fields = ['id', 'image', 'birthLastName', 'currentLastName', 'firstName', 'birthDate', 'birthPlace',
                  'residence', 'passportNumber', 'passportIssueDate', 'passportExpirationDate',
                  'passportIssuingAuthority', 'email', 'password', 'height', 'weight', 'englishLevel',
                  'familyStatus', 'country', 'education', 'driving_licence', 'experience', 'partners',
                  'status', 'mother', 'father', 'contact', 'children', 'referal', 'workers', 'notes',
                  'uploaded_at', 'last_modified', 'related_clients' ]

        extra_kwargs = {
            'image': {'required': False}
        }

    def validate_image(self, value):
        return value



    def create(self, validated_data):
        mother_data = self.initial_data.get('mother')
        father_data = self.initial_data.get('father')
        contact_data = self.initial_data.get('contact')
        children_data = self.initial_data.get('children', [])
        partners_data = self.initial_data.get('partners', [])
        related_clients_data = self.initial_data.get('related_clients', [])
        related_clients_data = validated_data.pop('related_clients', [])


        if isinstance(mother_data, str):
            mother_data = json.loads(mother_data)
        if isinstance(father_data, str):
            father_data = json.loads(father_data)
        if isinstance(contact_data, str):
            contact_data = json.loads(contact_data)
        if isinstance(children_data, str):
            children_data = json.loads(children_data)

        if isinstance(partners_data, str):
            partners_data = json.loads(partners_data)


        client = Client.objects.create(**validated_data)

        if mother_data:
            Mother.objects.create(client=client, **mother_data)
        if father_data:
            Father.objects.create(client=client, **father_data)
        if contact_data:
            Contact.objects.create(client=client, **contact_data)

        for child_data in children_data:
            Child.objects.create(client=client, **child_data)


        for partner_data in partners_data:
            name_partner_name = partner_data.pop('name_partner', None)
            name_partner = PartnerClass.objects.get(name=name_partner_name) if name_partner_name else None
            Partner.objects.create(client=client, name_partner=name_partner, **partner_data)


        if related_clients_data:
            client.related_clients.set(related_clients_data)

        return client

    def update(self, instance, validated_data):
        mother_data = self.initial_data.get('mother', None)
        father_data = self.initial_data.get('father', None)
        contact_data = self.initial_data.get('contact', None)
        children_data = self.initial_data.get('children', [])
        partners_data = self.initial_data.get('partners', [])
        related_clients_data = validated_data.pop('related_clients', None)



        if isinstance(mother_data, str):
            mother_data = json.loads(mother_data)
        if isinstance(father_data, str):
            father_data = json.loads(father_data)
        if isinstance(contact_data, str):
            contact_data = json.loads(contact_data)
        if isinstance(children_data, str):
            children_data = json.loads(children_data)

        if isinstance(partners_data, str):
            partners_data = json.loads(partners_data)

        # if isinstance(related_clients_data, str):
        #     related_clients_data = json.loads(related_clients_data)

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

        existing_partner_ids = [partner.id for partner in instance.partners.all()]
        incoming_partner_ids = [item['id'] for item in partners_data if 'id' in item]

        for partner_id in set(existing_partner_ids) - set(incoming_partner_ids):
            Partner.objects.filter(id=partner_id).delete()

        for partner_data in partners_data:
            partner_id = partner_data.get('id', None)
            name_partner_name = partner_data.pop('name_partner', None)
            name_partner = PartnerClass.objects.get(name=name_partner_name) if name_partner_name else None

            if partner_id:
                partner = Partner.objects.get(id=partner_id, client=instance)
                partner.name_partner = name_partner
                for key, value in partner_data.items():
                    setattr(partner, key, value)
                partner.save()
            else:
                Partner.objects.create(client=instance, name_partner=name_partner, **partner_data)

        if related_clients_data is not None:
            instance.related_clients.set(related_clients_data)

        instance.save()
        return instance
