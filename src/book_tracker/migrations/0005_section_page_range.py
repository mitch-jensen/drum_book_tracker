from django.db import migrations, models


def populate_section_page_ranges(apps, schema_editor):
    Book = apps.get_model("book_tracker", "Book")

    for book in Book.objects.all():
        sections = list(book.sections.order_by("order", "pk"))
        if not sections:
            continue

        current_page = 1
        for index, section in enumerate(sections):
            remaining_sections = len(sections) - index
            remaining_pages = max(book.page_count - current_page + 1, remaining_sections)
            pages_for_section = max(1, remaining_pages // remaining_sections)
            end_page = min(book.page_count, current_page + pages_for_section - 1)
            if index == len(sections) - 1:
                end_page = book.page_count

            section.start_page = min(current_page, book.page_count)
            section.end_page = max(section.start_page, end_page)
            section.save(update_fields=["start_page", "end_page"])
            current_page = min(section.end_page + 1, book.page_count)


class Migration(migrations.Migration):
    dependencies = [
        ("book_tracker", "0004_remove_exercise_notation_musicxml"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="end_page",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="section",
            name="start_page",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.RunPython(populate_section_page_ranges, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="section",
            constraint=models.CheckConstraint(
                condition=models.Q(start_page__lte=models.F("end_page")),
                name="section_start_page_lte_end_page",
            ),
        ),
    ]
