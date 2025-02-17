import pytest
from pytz import timezone
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware, datetime

from baserow.contrib.database.fields.field_types import DateFieldType
from baserow.contrib.database.fields.models import DateField
from baserow.contrib.database.fields.handler import FieldHandler
from baserow.contrib.database.rows.handler import RowHandler


@pytest.mark.django_db
def test_date_field_type_prepare_value(data_fixture):
    d = DateFieldType()

    f = data_fixture.create_date_field(date_include_time=True)
    amsterdam = timezone('Europe/Amsterdam')
    utc = timezone('UTC')
    expected_date = make_aware(datetime(2020, 4, 10, 0, 0, 0), utc)
    expected_datetime = make_aware(datetime(2020, 4, 10, 12, 30, 30), utc)

    with pytest.raises(ValidationError):
        assert d.prepare_value_for_db(f, 'TEST')

    assert d.prepare_value_for_db(f, None) is None

    unprepared_datetime = make_aware(datetime(2020, 4, 10, 14, 30, 30), amsterdam)
    assert d.prepare_value_for_db(f, unprepared_datetime) == expected_datetime

    unprepared_datetime = make_aware(datetime(2020, 4, 10, 12, 30, 30), utc)
    assert d.prepare_value_for_db(f, unprepared_datetime) == expected_datetime

    unprepared_datetime = datetime(2020, 4, 10, 12, 30, 30)
    assert d.prepare_value_for_db(f, unprepared_datetime) == expected_datetime

    unprepared_date = date(2020, 4, 10)
    assert d.prepare_value_for_db(f, unprepared_date) == expected_date

    assert d.prepare_value_for_db(f, '2020-04-10') == expected_date
    assert d.prepare_value_for_db(f, '2020-04-11') != expected_date
    assert d.prepare_value_for_db(f, '2020-04-10 12:30:30') == expected_datetime
    assert d.prepare_value_for_db(f, '2020-04-10 00:30:30 PM') == expected_datetime

    f = data_fixture.create_date_field(date_include_time=False)
    expected_date = date(2020, 4, 10)

    unprepared_datetime = datetime(2020, 4, 10, 14, 30, 30)
    assert d.prepare_value_for_db(f, unprepared_datetime) == expected_date

    unprepared_datetime = make_aware(datetime(2020, 4, 10, 14, 30, 30), amsterdam)
    assert d.prepare_value_for_db(f, unprepared_datetime) == expected_date

    assert d.prepare_value_for_db(f, '2020-04-10') == expected_date
    assert d.prepare_value_for_db(f, '2020-04-11') != expected_date
    assert d.prepare_value_for_db(f, '2020-04-10 12:30:30') == expected_date
    assert d.prepare_value_for_db(f, '2020-04-10 00:30:30 PM') == expected_date


@pytest.mark.django_db
def test_date_field_type(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)

    field_handler = FieldHandler()
    row_handler = RowHandler()

    amsterdam = timezone('Europe/Amsterdam')
    utc = timezone('utc')

    date_field_1 = field_handler.create_field(user=user, table=table, type_name='date',
                                              name='Date')
    date_field_2 = field_handler.create_field(user=user, table=table, type_name='date',
                                              name='Datetime', date_include_time=True)

    assert date_field_1.date_include_time is False
    assert date_field_2.date_include_time is True
    assert len(DateField.objects.all()) == 2

    model = table.get_model(attribute_names=True)

    row = row_handler.create_row(user=user, table=table, values={}, model=model)
    assert row.date is None
    assert row.datetime is None

    row = row_handler.create_row(user=user, table=table, values={
        'date': '2020-4-1',
        'datetime': '2020-4-1 12:30:30'
    }, model=model)
    row.refresh_from_db()
    assert row.date == date(2020, 4, 1)
    assert row.datetime == datetime(2020, 4, 1, 12, 30, 30, tzinfo=utc)

    row = row_handler.create_row(user=user, table=table, values={
        'datetime': make_aware(datetime(2020, 4, 1, 12, 30, 30), amsterdam)
    }, model=model)
    row.refresh_from_db()
    assert row.date is None
    assert row.datetime == datetime(2020, 4, 1, 10, 30, 30, tzinfo=timezone('UTC'))

    date_field_1 = field_handler.update_field(user=user, field=date_field_1,
                                              date_include_time=True)
    date_field_2 = field_handler.update_field(user=user, field=date_field_2,
                                              date_include_time=False)

    assert date_field_1.date_include_time is True
    assert date_field_2.date_include_time is False

    model = table.get_model(attribute_names=True)
    rows = model.objects.all()

    assert rows[0].date is None
    assert rows[0].datetime is None
    assert rows[1].date == datetime(2020, 4, 1, tzinfo=timezone('UTC'))
    assert rows[1].datetime == date(2020, 4, 1)
    assert rows[2].date is None
    assert rows[2].datetime == date(2020, 4, 1)

    field_handler.delete_field(user=user, field=date_field_1)
    field_handler.delete_field(user=user, field=date_field_2)

    assert len(DateField.objects.all()) == 0


@pytest.mark.django_db
def test_converting_date_field_value(data_fixture):
    user = data_fixture.create_user()
    table = data_fixture.create_database_table(user=user)

    field_handler = FieldHandler()
    row_handler = RowHandler()
    utc = timezone('utc')

    date_field_eu = data_fixture.create_text_field(table=table)
    date_field_us = data_fixture.create_text_field(table=table)
    date_field_iso = data_fixture.create_text_field(table=table)
    date_field_eu_12 = data_fixture.create_text_field(table=table)
    date_field_us_12 = data_fixture.create_text_field(table=table)
    date_field_iso_12 = data_fixture.create_text_field(table=table)
    date_field_eu_24 = data_fixture.create_text_field(table=table)
    date_field_us_24 = data_fixture.create_text_field(table=table)
    date_field_iso_24 = data_fixture.create_text_field(table=table)

    model = table.get_model()
    row_handler.create_row(user=user, table=table, model=model, values={
        f'field_{date_field_eu.id}': '22/07/2021',
        f'field_{date_field_us.id}': '07/22/2021',
        f'field_{date_field_iso.id}': '2021-07-22',
        f'field_{date_field_eu_12.id}': '22/07/2021 12:45 PM',
        f'field_{date_field_us_12.id}': '07/22/2021 12:45 PM',
        f'field_{date_field_iso_12.id}': '2021-07-22 12:45 PM',
        f'field_{date_field_eu_24.id}': '22/07/2021 12:45',
        f'field_{date_field_us_24.id}': '07/22/2021 12:45',
        f'field_{date_field_iso_24.id}': '2021-07-22 12:45',
    })
    row_handler.create_row(user=user, table=table, model=model, values={
        f'field_{date_field_eu.id}': '22-7-2021',
        f'field_{date_field_us.id}': '7-22-2021',
        f'field_{date_field_iso.id}': '2021/7/22',
        f'field_{date_field_eu_12.id}': '22-7-2021 12:45am',
        f'field_{date_field_us_12.id}': '7-22-2021 12:45am',
        f'field_{date_field_iso_12.id}': '2021/7/22 12:45am',
        f'field_{date_field_eu_24.id}': '22-7-2021 7:45',
        f'field_{date_field_us_24.id}': '7-22-2021 7:45',
        f'field_{date_field_iso_24.id}': '2021/7/22 7:45',
    })
    row_handler.create_row(user=user, table=table, model=model, values={
        f'field_{date_field_eu.id}': '22/07/2021 12:00',
        f'field_{date_field_us.id}': '07/22/2021 12:00am',
        f'field_{date_field_iso.id}': '2021-07-22 12:00 PM',
        f'field_{date_field_eu_12.id}': 'INVALID',
        f'field_{date_field_us_12.id}': '2222-2222-2222',
        f'field_{date_field_iso_12.id}': 'x-7--1',
        f'field_{date_field_eu_24.id}': '22-7-2021 7:45:12',
        f'field_{date_field_us_24.id}': '7-22-2021 7:45:23',
        f'field_{date_field_iso_24.id}': '2021/7/22 7:45:70'
    })
    row_handler.create_row(user=user, table=table, model=model, values={
        f'field_{date_field_eu.id}': '2018-08-20T13:20:10',
        f'field_{date_field_us.id}': '2017 Mar 03 05:12:41.211',
        f'field_{date_field_iso.id}': '19/Apr/2017:06:36:15',
        f'field_{date_field_eu_12.id}': 'Dec 2, 2017 2:39:58 AM',
        f'field_{date_field_us_12.id}': 'Jun 09 2018 15:28:14',
        f'field_{date_field_iso_12.id}': 'Apr 20 00:00:35 2010',
        f'field_{date_field_eu_24.id}': 'Apr 20 00:00:35 2010',
        f'field_{date_field_us_24.id}': '2018-02-27 15:35:20.311',
        f'field_{date_field_iso_24.id}': '10-04-19 12:00:17'
    })

    date_field_eu = field_handler.update_field(
        user=user, field=date_field_eu, new_type_name='date', date_format='EU'
    )
    date_field_us = field_handler.update_field(
        user=user, field=date_field_us, new_type_name='date', date_format='US'
    )
    date_field_iso = field_handler.update_field(
        user=user, field=date_field_iso, new_type_name='date', date_format='ISO'
    )
    date_field_eu_12 = field_handler.update_field(
        user=user, field=date_field_eu_12, new_type_name='date', date_format='EU',
        date_include_time=True, date_time_format='12'
    )
    date_field_us_12 = field_handler.update_field(
        user=user, field=date_field_us_12, new_type_name='date', date_format='US',
        date_include_time=True, date_time_format='12'
    )
    date_field_iso_12 = field_handler.update_field(
        user=user, field=date_field_iso_12, new_type_name='date', date_format='ISO',
        date_include_time=True, date_time_format='12'
    )
    date_field_eu_24 = field_handler.update_field(
        user=user, field=date_field_eu_24, new_type_name='date', date_format='EU',
        date_include_time=True, date_time_format='24'
    )
    date_field_us_24 = field_handler.update_field(
        user=user, field=date_field_us_24, new_type_name='date', date_format='US',
        date_include_time=True, date_time_format='24'
    )
    date_field_iso_24 = field_handler.update_field(
        user=user, field=date_field_iso_24, new_type_name='date', date_format='ISO',
        date_include_time=True, date_time_format='24'
    )

    model = table.get_model()
    rows = model.objects.all()

    assert getattr(rows[0], f'field_{date_field_eu.id}') == date(2021, 7, 22)
    assert getattr(rows[0], f'field_{date_field_us.id}') == date(2021, 7, 22)
    assert getattr(rows[0], f'field_{date_field_iso.id}') == date(2021, 7, 22)
    assert getattr(rows[0], f'field_{date_field_eu_12.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[0], f'field_{date_field_us_12.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[0], f'field_{date_field_iso_12.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[0], f'field_{date_field_eu_24.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[0], f'field_{date_field_us_24.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[0], f'field_{date_field_iso_24.id}') == (
        datetime(2021, 7, 22, 12, 45, 0, tzinfo=utc)
    )

    assert getattr(rows[1], f'field_{date_field_eu.id}') == date(2021, 7, 22)
    assert getattr(rows[1], f'field_{date_field_us.id}') == date(2021, 7, 22)
    assert getattr(rows[1], f'field_{date_field_iso.id}') == date(2021, 7, 22)
    assert getattr(rows[1], f'field_{date_field_eu_12.id}') == (
        datetime(2021, 7, 22, 0, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[1], f'field_{date_field_us_12.id}') == (
        datetime(2021, 7, 22, 0, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[1], f'field_{date_field_iso_12.id}') == (
        datetime(2021, 7, 22, 0, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[1], f'field_{date_field_eu_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[1], f'field_{date_field_us_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[1], f'field_{date_field_iso_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )

    assert getattr(rows[2], f'field_{date_field_eu.id}') == date(2021, 7, 22)
    assert getattr(rows[2], f'field_{date_field_us.id}') == date(2021, 7, 22)
    assert getattr(rows[2], f'field_{date_field_iso.id}') == date(2021, 7, 22)
    assert getattr(rows[2], f'field_{date_field_eu_12.id}') is None
    assert getattr(rows[2], f'field_{date_field_us_12.id}') is None
    assert getattr(rows[2], f'field_{date_field_iso_12.id}') is None
    assert getattr(rows[2], f'field_{date_field_eu_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[2], f'field_{date_field_us_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )
    assert getattr(rows[2], f'field_{date_field_iso_24.id}') == (
        datetime(2021, 7, 22, 7, 45, 0, tzinfo=utc)
    )

    """
    f'field_{date_field_eu.id}': '2018-08-20T13:20:10',
    f'field_{date_field_us.id}': '2017 Mar 03 05:12:41.211',
    f'field_{date_field_iso.id}': '19/Apr/2017:06:36:15',
    f'field_{date_field_eu_12.id}': 'Dec 2, 2017 2:39:58 AM',
    f'field_{date_field_us_12.id}': 'Jun 09 2018 15:28:14',
    f'field_{date_field_iso_12.id}': 'Apr 20 00:00:35 2010',
    f'field_{date_field_eu_24.id}': 'Apr 20 00:00:35 2010',
    f'field_{date_field_us_24.id}': '2018-02-27 15:35:20.311',
    f'field_{date_field_iso_24.id}': '10-04-19 12:00:17'
    """

    assert getattr(rows[3], f'field_{date_field_eu.id}') == date(2018, 8, 20)
    assert getattr(rows[3], f'field_{date_field_us.id}') == date(2017, 3, 3)
    assert getattr(rows[3], f'field_{date_field_iso.id}') == date(2017, 4, 19)
    assert getattr(rows[3], f'field_{date_field_eu_12.id}') == (
        datetime(2017, 12, 2, 2, 39, 58, tzinfo=utc)
    )
    assert getattr(rows[3], f'field_{date_field_us_12.id}') == (
        datetime(2018, 6, 9, 15, 28, 14, tzinfo=utc)
    )
    assert getattr(rows[3], f'field_{date_field_iso_12.id}') == (
        datetime(2010, 4, 20, 0, 0, 35, tzinfo=utc)
    )
    assert getattr(rows[3], f'field_{date_field_eu_24.id}') == (
        datetime(2010, 4, 20, 0, 0, 35, tzinfo=utc)
    )
    assert getattr(rows[3], f'field_{date_field_us_24.id}') == (
        datetime(2018, 2, 27, 15, 35, 20, 311000, tzinfo=utc)
    )
    assert getattr(rows[3], f'field_{date_field_iso_24.id}') == (
        datetime(10, 4, 19, 12, 0, tzinfo=utc)
    )

    date_field_eu = field_handler.update_field(
        user=user, field=date_field_eu, new_type_name='text'
    )
    date_field_us = field_handler.update_field(
        user=user, field=date_field_us, new_type_name='text'
    )
    date_field_iso = field_handler.update_field(
        user=user, field=date_field_iso, new_type_name='text'
    )
    date_field_eu_12 = field_handler.update_field(
        user=user, field=date_field_eu_12, new_type_name='text'
    )
    date_field_us_12 = field_handler.update_field(
        user=user, field=date_field_us_12, new_type_name='text'
    )
    date_field_iso_12 = field_handler.update_field(
        user=user, field=date_field_iso_12, new_type_name='text'
    )
    date_field_eu_24 = field_handler.update_field(
        user=user, field=date_field_eu_24, new_type_name='text'
    )
    date_field_us_24 = field_handler.update_field(
        user=user, field=date_field_us_24, new_type_name='text'
    )
    date_field_iso_24 = field_handler.update_field(
        user=user, field=date_field_iso_24, new_type_name='text'
    )

    model = table.get_model()
    rows = model.objects.all()

    assert getattr(rows[0], f'field_{date_field_eu.id}') == '22/07/2021'
    assert getattr(rows[0], f'field_{date_field_us.id}') == '07/22/2021'
    assert getattr(rows[0], f'field_{date_field_iso.id}') == '2021-07-22'
    assert getattr(rows[0], f'field_{date_field_eu_12.id}') == '22/07/2021 12:45PM'
    assert getattr(rows[0], f'field_{date_field_us_12.id}') == '07/22/2021 12:45PM'
    assert getattr(rows[0], f'field_{date_field_iso_12.id}') == '2021-07-22 12:45PM'
    assert getattr(rows[0], f'field_{date_field_eu_24.id}') == '22/07/2021 12:45'
    assert getattr(rows[0], f'field_{date_field_us_24.id}') == '07/22/2021 12:45'
    assert getattr(rows[0], f'field_{date_field_iso_24.id}') == '2021-07-22 12:45'

    assert getattr(rows[2], f'field_{date_field_eu_12.id}') is None
