from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Transactions
from .utils import ServerSeedGenerator
import logging

logger = logging.getLogger(__name__)

def get_new_crash_point(request):
    seed_generator = ServerSeedGenerator()
    seed_generator.generate_hash()
    seed_generator.crash_point_from_hash()
    
    crash_point = seed_generator.get_crash_point()
    
    return JsonResponse({'crash_point': crash_point})
class Home(TemplateView):
    model = Transactions
    template_name = 'index.html'
    context_object_name = 'items'

    def get_new_crash_point(self):
        seed_generator = ServerSeedGenerator()

        # Generate hash and crash point using the generated server seed
        seed_generator.generate_hash()
        seed_generator.crash_point_from_hash()

        # Get the generated hash and crash point
        self.generated_hash = seed_generator.get_generated_hash()
        self.crash_point = seed_generator.get_crash_point()

        # Print the new crash point (optional)
        print(self.crash_point)

        # Return the new crash point as JSON response
        return JsonResponse({'crash_point': self.crash_point})

    def get_context_data(self, **kwargs):
        # Fetch and add the Transactions objects to the context
        items = self.model.objects.all()

        # Initialize generated_hash and crash_point if not set
        if not hasattr(self, 'generated_hash') or not hasattr(self, 'crash_point'):
            self.get_new_crash_point()

        # Add the generated_hash and crash_point to the context
        context = super().get_context_data(**kwargs)
        context['generated_hash'] = self.generated_hash
        context['crash_point'] = self.crash_point
        context['items'] = items

        # Logging and debugging
        logger.debug("Total items fetched: %d", items.count())

        return context
