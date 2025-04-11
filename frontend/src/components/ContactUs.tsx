const ContactUs = () => {
    return (
      <section id="contact" className="px-6 py-16 bg-[#f4f4fc] text-center">
        <h2 className="text-3xl font-bold text-[#361899] mb-4 underline decoration-green-400 underline-offset-4">
          Contact Us
        </h2>
        <p className="text-gray-700 text-lg">
          Please reach us at:{" "}
          <span
            // href="mailto:ram@noha.ai"
            className="text-[#0B9284] font-semibold hover:underline"
          >
            ram@noha.ai
          </span>
        </p>
      </section>
    );
  };
  
  export default ContactUs;
  