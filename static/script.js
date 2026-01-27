const symptomsList = [
    'itching','skin_rash','nodal_skin_eruptions','continuous_sneezing','shivering',
    'chills','joint_pain','stomach_pain','acidity','ulcers_on_tongue','muscle_wasting',
    'vomiting','burning_micturition','spotting_ urination','fatigue','weight_gain',
    'anxiety','cold_hands_and_feets','mood_swings','weight_loss','restlessness',
    'lethargy','patches_in_throat','irregular_sugar_level','cough','high_fever',
    'sunken_eyes','breathlessness','sweating','dehydration','indigestion','headache',
    'yellowish_skin','dark_urine','nausea','loss_of_appetite','pain_behind_the_eyes',
    'back_pain','constipation','abdominal_pain','diarrhoea','mild_fever','yellow_urine',
    'yellowing_of_eyes','acute_liver_failure','fluid_overload','swelling_of_stomach',
    'swelled_lymph_nodes','malaise','blurred_and_distorted_vision','phlegm',
    'throat_irritation','redness_of_eyes','sinus_pressure','runny_nose','congestion',
    'chest_pain','weakness_in_limbs','fast_heart_rate','pain_during_bowel_movements',
    'pain_in_anal_region','bloody_stool','irritation_in_anus','neck_pain','dizziness',
    'cramps','bruising','obesity','swollen_legs','swollen_blood_vessels',
    'puffy_face_and_eyes','enlarged_thyroid','brittle_nails','swollen_extremeties',
    'excessive_hunger','extra_marital_contacts','drying_and_tingling_lips',
    'slurred_speech','knee_pain','hip_joint_pain','muscle_weakness','stiff_neck',
    'swelling_joints','movement_stiffness','spinning_movements','loss_of_balance',
    'unsteadiness','weakness_of_one_body_side','loss_of_smell','bladder_discomfort',
    'foul_smell_of urine','continuous_feel_of_urine','passage_of_gases',
    'internal_itching','toxic_look_(typhos)','depression','irritability','muscle_pain',
    'altered_sensorium','red_spots_over_body','belly_pain','abnormal_menstruation',
    'dischromic _patches','watering_from_eyes','increased_appetite','polyuria',
    'family_history','mucoid_sputum','rusty_sputum','lack_of_concentration',
    'visual_disturbances','receiving_blood_transfusion',
    'receiving_unsterile_injections','coma','stomach_bleeding',
    'distention_of_abdomen','history_of_alcohol_consumption','fluid_overload.1',
    'blood_in_sputum','prominent_veins_on_calf','palpitations','painful_walking',
    'pus_filled_pimples','blackheads','scurring','skin_peeling','silver_like_dusting',
    'small_dents_in_nails','inflammatory_nails','blister','red_sore_around_nose',
    'yellow_crust_ooze'
];

const input = document.getElementById('symptomInput');
const dropdown = document.getElementById('dropdownList');
const tagsContainer = document.getElementById('selectedTags');
const btn = document.getElementById('analyze-btn');
const statusMsg = document.getElementById('statusMsg');
const hiddenInput = document.getElementById("hiddenSymptoms"); // Ensure ID matches HTML
const form = document.getElementById("predictForm"); // Use ID for better selection

let selectedSymptoms = [];

// ---------------- FILTER DROPDOWN ----------------
input.addEventListener('input', (e) => {
    const value = e.target.value.toLowerCase();
    dropdown.innerHTML = '';
    if (!value) { dropdown.style.display = 'none'; return; }

    const filtered = symptomsList.filter(
        s => s.toLowerCase().includes(value) && !selectedSymptoms.includes(s)
    );

    dropdown.style.display = filtered.length ? 'block' : 'none';

    filtered.forEach(s => {
        const item = document.createElement('div');
        item.classList.add('dropdown-item');
        item.textContent = s.replace(/_/g, ' ');
        item.onclick = () => addSymptom(s);
        dropdown.appendChild(item);
    });
});

// Auto-hide flash messages after 5 seconds
setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);
// This script finds any alert and removes it after 4 seconds
document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = "opacity 0.8s ease, transform 0.8s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-20px)";
            setTimeout(() => alert.remove(), 800);
        }, 4000); // 4 seconds of display time
    });
});

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}



// ---------------- ADD / REMOVE ----------------
function addSymptom(symptom) {
    if(!selectedSymptoms.includes(symptom)) {
        selectedSymptoms.push(symptom);
        renderTags();
    }
    input.value = '';
    dropdown.style.display = 'none';
}

function removeSymptom(symptom) {
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);
    renderTags();
}

// ---------------- RENDER TAGS ----------------
function renderTags() {
    tagsContainer.innerHTML = '';

    selectedSymptoms.forEach(s => {
        const tag = document.createElement('div');
        tag.classList.add('tag');
        tag.innerHTML = `${s.replace(/_/g, ' ')} <span onclick="removeSymptom('${s}')">&times;</span>`;
        tagsContainer.appendChild(tag);
    });

    // Update hidden input every time tags change
    if (hiddenInput) {
        hiddenInput.value = selectedSymptoms.join(",");
        // DEBUG LOG:
        console.log("Hidden input value update:", hiddenInput.value);
    }

    btn.disabled = selectedSymptoms.length === 0;
    statusMsg.style.display = selectedSymptoms.length ? 'none' : 'block';
}

// ---------------- FORM SUBMISSION ----------------
if (form) {
    form.addEventListener("submit", (e) => {
        // Final check: set the hidden value again just before submission
        hiddenInput.value = selectedSymptoms.join(",");
        console.log("Final submission data:", hiddenInput.value);
        
        // Optional: Show a loading state on the button
        btn.innerText = "Analyzing...";
        btn.style.opacity = "0.7";
    });
}

// ---------------- CLOSE DROPDOWN ----------------
document.addEventListener('click', (e) => {
    if (e.target !== input) dropdown.style.display = 'none';
});