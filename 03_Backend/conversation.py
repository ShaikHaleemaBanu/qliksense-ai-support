class ConversationState:

    def __init__(self):
        self.category = None
        self.current_step = 0

        # Troubleshooting state
        self.resolved = False
        self.awaiting_resolution = False

        # Ticket suggestion state
        self.ticket_required = False

        # Ticket information collection state
        self.ticket_collection_active = False
        self.ticket_information_complete = False

        # Ticket information
        self.ticket_data = {}
        self.ticket_field_index = 0

        # Troubleshooting history
        self.attempted_steps = []

    # =====================================================
    # RESET CONVERSATION
    # =====================================================

    def reset(self):

        self.category = None
        self.current_step = 0

        self.resolved = False
        self.awaiting_resolution = False

        self.ticket_required = False

        self.ticket_collection_active = False
        self.ticket_information_complete = False

        self.ticket_data = {}
        self.ticket_field_index = 0

        self.attempted_steps = []

    # =====================================================
    # START NORMAL TROUBLESHOOTING
    # =====================================================

    def start(self, category):

        self.category = category
        self.current_step = 0

        self.resolved = False
        self.awaiting_resolution = True

        self.ticket_required = False

        self.ticket_collection_active = False
        self.ticket_information_complete = False

        self.ticket_data = {}
        self.ticket_field_index = 0

        self.attempted_steps = []

    # =====================================================
    # START TICKET INFORMATION COLLECTION
    # =====================================================

    def start_ticket_collection(self):

        self.category = "incorrect_ticket"
        self.current_step = 0

        self.resolved = False
        self.awaiting_resolution = False

        self.ticket_required = False

        self.ticket_collection_active = True
        self.ticket_information_complete = False

        self.ticket_data = {}
        self.ticket_field_index = 0

        self.attempted_steps = []

    # =====================================================
    # ADD TROUBLESHOOTING STEP
    # =====================================================

    def add_attempted_step(self, step):

        self.attempted_steps.append(step)

    # =====================================================
    # MOVE TO NEXT STEP
    # =====================================================

    def next_step(self):

        self.current_step += 1
        self.awaiting_resolution = True