document.addEventListener("DOMContentLoaded", function() {
    // Simulated API response
    const emails = [
        { from: "sender1@example.com", subject: "Subject 1", body: "This is the body of email 1." },
        { from: "sender2@example.com", subject: "Subject 2", body: "This is the body of email 2." },
        { from: "sender3@example.com", subject: "Subject 3", body: "This is the body of email 3." }
    ];

    // Display emails
    const emailsContainer = document.getElementById("emails-container");

    emails.forEach(email => {
        const emailDiv = document.createElement("div");
        emailDiv.classList.add("email");

        const emailHeader = document.createElement("div");
        emailHeader.classList.add("email-header");
        emailHeader.textContent = `From: ${email.from}, Subject: ${email.subject}`;

        const emailBody = document.createElement("div");
        emailBody.classList.add("email-body");
        emailBody.textContent = email.body;

        emailDiv.appendChild(emailHeader);
        emailDiv.appendChild(emailBody);
        emailsContainer.appendChild(emailDiv);
    });

    // Move emails container after header section
    const headerSection = document.getElementById("headerSection");
    const mainBody = document.getElementById("mainBody");
    mainBody.insertBefore(emailsContainer, headerSection.nextSibling);
});
