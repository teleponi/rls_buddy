document.addEventListener('alpine:init', () => {
    Alpine.data('myComponent', () => ({

        email: '',
        password: '',
        isAuthenticated: false,
        token: '',

        // tracking
        currentTrackingId: null,
        isTracking: false,
        trackingType: '',
        messageClass: '',
        message: '',


        // sleep
        sleepDate: '',
        sleepDuration: '',
        sleepQuality: 'good',
        sleepComment: '',
        selectedSymptoms: [],
        symptoms: [],

        // day
        dayDate: '',
        dayActivity: '',
        dayComment: '',
        late_morning_symptoms: [],
        afternoon_symptoms: [],
        triggers: [],
        selectedTriggers: [],
        selectedDaySymptoms: [],
        selectedAfternoonSymptoms: [],

        // Overview
        isOverview: false,
        trackingOverview: [],

        logout() {
            this.isAuthenticated = false;
            this.token = '';
            this.isTracking = false;
            this.isOverview = false;
            this.message = '';
            this.messageClass = '';
        },

        login() {
            fetch('http://127.0.0.1:8000/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${this.email}&password=${this.password}`,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.access_token) {
                        this.token = data.access_token;
                        this.isAuthenticated = true;
                        this.fetchSymptoms();
                        this.fetchTriggers();
                        this.message = '';
                    } else {
                        this.message = 'Login failed';
                        this.messageClass = 'bg-red-500 text-white p-2 rounded';
                    }
                })
        },

        fetchSymptoms() {
            fetch('http://127.0.0.1:8000/trackings/symptoms', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.symptoms = data;
                })
        },

        fetchTriggers() {
            fetch('http://127.0.0.1:8000/trackings/triggers', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.triggers = data;
                })
        },
        fetchOverviewx() {
            let url = `http://127.0.0.1:8000/trackings/me?type=${this.trackingType}`;
            console.log(url);

            fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.trackingOverview = data;
                })
        },

        async fetchOverview() {

            let url = `http://127.0.0.1:8000/trackings/me?type=${this.trackingType}`;
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                    },
                });
                if (response.ok) {
                    const data = await response.json();
                    this.trackingOverview = data;
                } else {
                    this.message = "Failed to load data.";
                    this.messageClass = "text-red-500";
                }
            } catch (error) {
                this.message = "Failed to load data.";
                this.messageClass = "text-red-500";
            }
        },


        selectTracking(type) {
            this.trackingType = type;
            this.isTracking = true;
            this.isOverview = false;
        },

        selectOverview(type) {
            this.trackingType = type;
            this.isOverview = true;
            this.isTracking = false;
            this.fetchOverview();
            this.message = '';
            this.messageClass = '';

        },

        clearSleepForm() {
            this.sleepDate = '';
            this.sleepDuration = '';
            this.sleepQuality = 'good';
            this.sleepComment = '';
            this.selectedSymptoms = [];
        },
        clearDayForm() {
            this.dayDate = '';
            this.dayComment = '';
            this.selectedDaySymptoms = [];
            this.selectedAfternoonSymptoms = [];
            this.selectedTriggers = [];
        },


        async deleteSleepTracking(index) {
            const tracking = this.trackingOverview[index];
            this.currentTrackingId = tracking.id;
            this.trackingOverview.splice(index, 1);

            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/sleep/${this.currentTrackingId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`,
                    }
                });
                if (response.ok) {
                    this.message = "Sleep entry deleted successfully.";
                    this.messageClass = "text-green-500";
                } else {
                    this.message = "Failed to delete sleep entry.";
                    this.messageClass = "text-red-500";
                }

            } catch (error) {
                this.message = "Failed to delete sleep entry.";
                this.messageClass = "text-red-500";
            }
        },

        async deleteDayTracking(index) {
            const tracking = this.trackingOverview[index];
            this.currentTrackingId = tracking.id;
            this.trackingOverview.splice(index, 1);

            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/day/${this.currentTrackingId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`,
                    }
                });
                if (response.ok) {
                    this.message = "day entry deleted successfully.";
                    this.messageClass = "text-green-500";
                } else {
                    this.message = "Failed to delete day entry.";
                    this.messageClass = "text-red-500";
                }

            } catch (error) {
                this.message = "Failed to delete day entry.";
                this.messageClass = "text-red-500";
            }
        },


        async editSleepTracking(index) {
            this.isTracking = true; // Show the form
            this.isOverview = false;
            const tracking = this.trackingOverview[index];
            this.currentTrackingId = tracking.id;  // Set the current tracking ID for later use

            // Fetch data from API
            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/sleep/${this.currentTrackingId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`,
                    }
                });
                const data = await response.json();
                const formattedDate = new Date(data.date).toISOString().split('T')[0];

                // Populate form with data
                this.sleepDate = formattedDate;
                this.sleepDuration = data.duration;
                this.sleepQuality = data.quality;
                this.sleepComment = data.comment;
                this.selectedSymptoms = data.symptoms.map(s => s.id); // Assuming symptoms are objects with id and name

            } catch (error) {
                this.message = "Failed to load tracking data.";
                this.messageClass = "text-red-500";
            }
        },

        async submitUpdateSleepEntry() {
            try {
                let body = JSON.stringify({
                    duration: this.sleepDuration,
                    quality: this.sleepQuality,
                    comment: this.sleepComment,
                    symptoms: this.selectedSymptoms,
                })

                const response = await fetch(`http://127.0.0.1:8000/trackings/sleep/${this.currentTrackingId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}` // Assume token is available
                    },
                    body: body
                });

                if (response.ok) {
                    this.message = "Sleep entry updated successfully.";
                    this.messageClass = "text-green-500";
                    this.clearSleepForm();
                    this.currentTrackingId = null;
                    this.isTracking = false;
                    //this.isOverview = true;  // Show the overview again
                } else {
                    this.message = "Failed to update sleep entry.";
                    this.messageClass = "text-red-500";
                }

            } catch (error) {
                this.message = "Error occurred while updating sleep entry.";
                this.messageClass = "text-red-500";
            }
        },

        async submitSleepEntry() {

            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/sleep`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}` // Assume token is available
                    },
                    body: JSON.stringify({
                        date: this.sleepDate,
                        duration: this.sleepDuration,
                        quality: this.sleepQuality,
                        comment: this.sleepComment,
                        symptoms: this.selectedSymptoms.map(Number),
                    })
                });
                if (response.ok) {
                    data = await response.json();
                    this.message = `Sleep entry ${data.id} added successfully`;
                    this.messageClass = 'bg-green-500 text-white p-2 rounded';
                    this.clearSleepForm();
                    //this.isTracking = false;
                } else {
                    this.message = `Failed to add sleep entry: ${data.detail}`
                    this.messageClass = 'bg-red-500 text-white p-2 rounded';
                }

            } catch (error) {
                this.message = "Error occurred while inserting sleep entry.";
                this.messageClass = "text-red-500";
            }
        },

        async submitDayEntry() {
            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/day`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}` // Assume token is available
                    },
                    body: JSON.stringify({
                        date: this.dayDate,
                        comment: this.dayComment,
                        late_morning_symptoms: this.selectedDaySymptoms.map(Number),
                        afternoon_symptoms: this.selectedAfternoonSymptoms.map(Number),
                        triggers: this.selectedTriggers.map(Number)
                    })
                });
                if (response.ok) {
                    data = await response.json();
                    this.message = `Day entry ${data.id} added successfully`;
                    this.messageClass = 'bg-green-500 text-white p-2 rounded';
                    this.clearDayForm();
                } else {
                    this.message = `Failed to add day entry: ${data.detail}`
                    this.messageClass = 'bg-red-500 text-white p-2 rounded';
                }

            } catch (error) {
                this.message = "Error occurred while inserting day entry.";
                this.messageClass = "text-red-500";
            }
        },

        async editDayTracking(index) {
            this.isTracking = true; // Show the form
            this.isOverview = false;
            const tracking = this.trackingOverview[index];
            this.currentTrackingId = tracking.id;

            // Fetch data from API
            try {
                const response = await fetch(`http://127.0.0.1:8000/trackings/day/${this.currentTrackingId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}`,
                    }
                });
                const data = await response.json();
                const formattedDate = new Date(data.date).toISOString().split('T')[0];

                // Populate form with data
                this.dayDate = formattedDate;
                this.dayComment = data.comment;
                this.selectedDaySymptoms = data.late_morning_symptoms.map(s => s.id);
                this.selectedAfternoonSymptoms = data.afternoon_symptoms.map(s => s.id);
                this.selectedTriggers = data.triggers.map(s => s.id);

            } catch (error) {
                this.message = "Failed to load tracking data.";
                this.messageClass = "text-red-500";
            }
        },
        async submitUpdateDayEntry() {
            try {
                let body = JSON.stringify({
                    date: this.dayDate,
                    comment: this.dayComment,
                    late_morning_symptoms: this.selectedDaySymptoms.map(Number),
                    afternoon_symptoms: this.selectedAfternoonSymptoms.map(Number),
                    triggers: this.selectedTriggers.map(Number)
                })

                const response = await fetch(`http://127.0.0.1:8000/trackings/day/${this.currentTrackingId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.token}` // Assume token is available
                    },
                    body: body
                });

                if (response.ok) {
                    this.message = "Day entry updated successfully.";
                    this.messageClass = "text-green-500";
                    this.clearDayForm();
                    this.currentTrackingId = null;
                    this.isTracking = false;
                } else {
                    this.message = "Failed to update day entry.";
                    this.messageClass = "text-red-500";
                }

            } catch (error) {
                this.message = "Error occurred while updating day entry.";
                this.messageClass = "text-red-500";
            }
        },

    }));
});
