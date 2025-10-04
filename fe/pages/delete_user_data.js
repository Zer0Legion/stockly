import { useState } from 'react';

export default function DeleteUserData() {
  const [email, setEmail] = useState('');
  const [reason, setReason] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      alert('Please provide your email address');
      return;
    }

    try {
      // You can either send this to your backend or use a service like EmailJS
      // For now, this creates a mailto link
      const subject = encodeURIComponent('Data Deletion Request - Stockly App');
      const body = encodeURIComponent(`
Email: ${email}
Reason for deletion: ${reason}
Date of request: ${new Date().toISOString()}

Please delete all my personal data associated with this email address from the Stockly application.
      `);
      
      window.location.href = `mailto:mikechunt981@gmail.com?subject=${subject}&body=${body}`;
      setSubmitted(true);
    } catch (error) {
      console.error('Error:', error);
      alert('There was an error processing your request. Please try again.');
    }
  };

  if (submitted) {
    return (
      <div style={{ 
        fontFamily: 'Arial, sans-serif', 
        maxWidth: '600px', 
        margin: '2rem auto', 
        padding: '2rem',
        lineHeight: '1.6'
      }}>
        <h1>Request Submitted</h1>
        <div style={{ 
          backgroundColor: '#d4edda', 
          border: '1px solid #c3e6cb', 
          borderRadius: '4px', 
          padding: '1rem', 
          marginBottom: '1rem' 
        }}>
          <p><strong>Your data deletion request has been submitted successfully.</strong></p>
          <p>We will process your request within 30 days and send you a confirmation email once your data has been deleted.</p>
        </div>
        <button 
          onClick={() => setSubmitted(false)}
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Submit Another Request
        </button>
      </div>
    );
  }

  return (
    <div style={{ 
      fontFamily: 'Arial, sans-serif', 
      maxWidth: '600px', 
      margin: '2rem auto', 
      padding: '2rem',
      lineHeight: '1.6'
    }}>
      <h1>Data Deletion Request</h1>
      
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        border: '1px solid #dee2e6', 
        borderRadius: '4px', 
        padding: '1rem', 
        marginBottom: '2rem' 
      }}>
        <h2>Your Privacy Rights</h2>
        <p>
          You have the right to request deletion of your personal data from our application. 
          This includes any information you've provided such as:
        </p>
        <ul>
          <li>Email addresses</li>
          <li>Names</li>
          <li>Stock preferences and watchlists</li>
          <li>Any other personal information collected by our app</li>
        </ul>
      </div>

      <div style={{ 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffeaa7', 
        borderRadius: '4px', 
        padding: '1rem', 
        marginBottom: '2rem' 
      }}>
        <h3>What Happens When You Request Deletion?</h3>
        <ol>
          <li>We will verify your identity to protect your privacy</li>
          <li>All your personal data will be permanently deleted from our systems within 30 days</li>
          <li>You will receive a confirmation email once the deletion is complete</li>
          <li>This action cannot be undone</li>
        </ol>
      </div>

      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <h3>Request Data Deletion</h3>
        
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
            placeholder="Enter the email address associated with your account"
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="reason" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Reason for Deletion (Optional)
          </label>
          <textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={4}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '1rem',
              resize: 'vertical'
            }}
            placeholder="Please let us know why you're requesting data deletion (optional)"
          />
        </div>

        <button
          type="submit"
          style={{
            backgroundColor: '#dc3545',
            color: 'white',
            padding: '0.75rem 1.5rem',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Request Data Deletion
        </button>
      </form>

      <div style={{ 
        fontSize: '0.9rem', 
        color: '#6c757d',
        borderTop: '1px solid #dee2e6',
        paddingTop: '1rem'
      }}>
        <h4>Contact Information</h4>
        <p>
          If you have any questions about this process or need assistance, please contact us at:
          <br />
          <strong>Email:</strong> mikechunt981@gmail.com
          <br />
          <strong>Response Time:</strong> We typically respond within 2-3 business days
        </p>
        
        <h4>Legal Compliance</h4>
        <p>
          This data deletion process is provided in compliance with applicable privacy laws 
          including GDPR, CCPA, and Facebook's Platform Policy requirements.
        </p>
      </div>
    </div>
  );
}