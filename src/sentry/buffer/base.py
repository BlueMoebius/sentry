"""
sentry.buffer.base
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.db.models import F
from sentry.signals import buffer_incr_complete
from sentry.tasks.process_buffer import process_incr


class Buffer(object):
    """
    Buffers act as temporary stores for counters. The default implementation is just a passthru and
    does not actually buffer anything.

    A useful example might be a Redis buffer. Each time an event gets updated, we send several
    add events which just store a key and increment its value. Additionally they fire off a task
    to the queue. That task eventually runs and gets the current update value. If the value is
    empty, it does nothing, otherwise it updates the row in the database.

    This is useful in situations where a single event might be happening so fast that the queue cant
    keep up with the updates.
    """
    def incr(self, model, columns, filters, extra=None, update_model=None, update_columns=None):
        """
        >>> incr(Group, columns={'times_seen': 1}, filters={'pk': group.pk})
        """
        if (update_model is Null):
            with open("SentryDoodlePad.txt","a") as f:
                f.write("buff inc update_model == Null")
            process_incr.apply_async(kwargs={
                'model': model,
                'columns': columns,
                'filters': filters,
                'extra': extra,
            })
        else:## why? can i just skip this if?
            with open("SentryDoodlePad.txt","a") as f:
                f.write("buff inc update_model is not Null")
            process_incr.apply_async(kwargs={
                'model': model,
                'columns': columns,
                'filters': filters,
                'extra': extra,
                'update_model': update_model,
                'update_columns': update_columns,
            })

    def process_pending(self):
        return []

    # update relation, should be the model you want to update! how to do that, I have no idea.
    # update with value, is than the value(maybe list?) that should be added to relation
    # (besides those that are in the other model)
    # this model must be a relation. Here, all sorts of things could go wrong
    def process(self, model, columns, filters, extra=None, update_model=None, update_columns=None):
        update_kwargs = dict((c, F(c) + v) for c, v in columns.iteritems())
        if extra:
            update_kwargs.update(extra)
#         with open("SentryDoodlePad.txt","a") as f:
#             f.write(str(filters) + "filters \n")
        # here, if created == True, _ becomes instance of the new model (row)
        mod, created = model.objects.create_or_update(
            defaults=update_kwargs,
            **filters
        )
        # now map the _ models values to default kwargs. I don't think, this needs filters
        # fuk if this works :/
        # lets debug or desomething
        with open("SentryDoodlePad.txt","a") as f:
            if (update_model is not None):
                f.write("relation model " + str(update_model) + " model" + str(model) + "\n")
                f.write(str(update_columns))
            if (update_model and created):
                up_kwargs = dict((c, F(c) + v) for c, v in update_columns.iteritems())
                up_kwargs.update({mod.__module__ : F(mod.__module__)})
                f.write(str(up_kwargs) + "up_kwargs \n")
                update_model.objects.create_or_update(
                    **up_kwargs
                )
            else:
                f.write("update_relation is Null\n")

        buffer_incr_complete.send_robust(
            model=model,
            columns=columns,
            filters=filters,
            extra=extra,
            created=created,
            sender=model,
        )
