from rest_framework import serializers
from .models import Client, Document, Payment, Refund, Mother, Father, Contact, Child


# class CountrySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Country
#         fields = ['id', 'name_country']


# class StatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Status
#         fields = ['id', 'name']


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ['id', 'file', 'title', 'uploaded_at']

    def create(self, validated_data):
        # Предполагаем, что client_id передается в контексте сериализатора
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        validated_data['client'] = client
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'title', 'uploaded_at']

    def create(self, validated_data):
        # Предполагаем, что client_id передается в контексте сериализатора
        client_id = self.context['view'].kwargs['client_id']
        client = Client.objects.get(id=client_id)
        validated_data['client'] = client
        return super().create(validated_data)


# class RefundSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Refund
#         fields = ['id', 'amount', 'title', 'uploaded_at']

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'amount', 'title', 'uploaded_at']

    def create(self, validated_data):
        # Предполагаем, что client_id передается в контексте сериализатора
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

    mother = MotherSerializer()
    father = FatherSerializer()
    contact = ContactSerializer()
    children = ChildSerializer(many=True, required=False)

    documents = DocumentSerializer(many=True, required=False)
    payment = PaymentSerializer(many=True, required=False)
    refund = RefundSerializer(many=True, required=False)


    class Meta:
        model = Client
        fields = [
            'id', 'image', 'birthLastName', 'currentLastName', 'firstName', 'birthDate', 'birthPlace', 'residence',
            'passportNumber', 'passportIssueDate', 'passportExpirationDate', 'passportIssuingAuthority',
            'email', 'password', 'height', 'weight', 'englishLevel', 'familyStatus', 'country',
            'status', 'mother', 'father', 'contact', 'children', 'documents', 'payment', 'refund',
            'uploaded_at', 'last_modified'
        ]

    # def create(self, validated_data):
    #     mother_data = validated_data.pop('mother')
    #     father_data = validated_data.pop('father')
    #     contact_data = validated_data.pop('contact')
    #     # countries_data = validated_data.pop('country', [])
    #     children_data = validated_data.pop('children', [])

    #     # Create the client first
    #     client = Client.objects.create(**validated_data)
    #     # if countries_data:
    #     #     client.country.set(countries_data)

    #     # Now create mother, father, and contact with reference to the client
    #     mother = Mother.objects.create(client=client, **mother_data)
    #     father = Father.objects.create(client=client, **father_data)
    #     contact = Contact.objects.create(client=client, **contact_data)

    #     # Handling children
    #     for child_data in children_data:
    #         Child.objects.create(client=client, **child_data)

    #     return super().create(validated_data)


    # def update(self, instance, validated_data):
    #     # Extract nested data first
    #     mother_data = validated_data.pop('mother', None)
    #     father_data = validated_data.pop('father', None)
    #     contact_data = validated_data.pop('contact', None)
    #     children_data = validated_data.pop('children', [])
    #     # countries_data = validated_data.pop('country', None)

    #     # Update the scalar fields
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     # Update the many-to-many relations
    #     # if countries_data is not None:
    #     #     instance.country.set(countries_data)

    #     # Handle nested updates or creations
    #     if mother_data:
    #         Mother.objects.update_or_create(client=instance, defaults=mother_data)
    #     if father_data:
    #         Father.objects.update_or_create(client=instance, defaults=father_data)
    #     if contact_data:
    #         Contact.objects.update_or_create(client=instance, defaults=contact_data)

    #     # Handle children
    #     existing_ids = [child.id for child in instance.children.all()]
    #     incoming_ids = [item['id'] for item in children_data if 'id' in item]

    #     # Delete children not included in the request
    #     for child_id in set(existing_ids) - set(incoming_ids):
    #         Child.objects.filter(id=child_id).delete()

    #     # Update existing children and create new ones
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
    #     return super().update(instance, validated_data)

    def create(self, validated_data):
        mother_data = validated_data.pop('mother')
        father_data = validated_data.pop('father')
        contact_data = validated_data.pop('contact')
        children_data = validated_data.pop('children', [])
        document_files = self.context['request'].FILES

        client = Client.objects.create(**validated_data)
        Mother.objects.create(client=client, **mother_data)
        Father.objects.create(client=client, **father_data)
        Contact.objects.create(client=client, **contact_data)

        for child_data in children_data:
            Child.objects.create(client=client, **child_data)

        for key, file in document_files.items():
            title = validated_data.get('title', '')
            Document.objects.create(client=client, file=file, title=title)

        return client

    def update(self, instance, validated_data):
        mother_data = validated_data.pop('mother', None)
        father_data = validated_data.pop('father', None)
        contact_data = validated_data.pop('contact', None)
        children_data = validated_data.pop('children', [])
        document_files = self.context['request'].FILES

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

        for key, file in document_files.items():
            title = validated_data.get('title', '')
            Document.objects.create(client=instance, file=file, title=title)

        instance.save()
        return instance
