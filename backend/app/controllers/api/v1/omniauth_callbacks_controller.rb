module Api
  module V1
    class OmniauthCallbacksController < ApplicationController
      allow_unauthenticated_access

      def google_oauth2
        auth = request.env['omniauth.auth']
        email = auth.info.email
        name = auth.info.name

        user = User.find_or_initialize_by(email_address: email)
        if user.new_record?
          user.name = name
          # Set a random password for OAuth users since they log in via Google
          user.password = SecureRandom.hex(16)
          user.role = 'standard'
          user.save!
        end

        session_record = user.sessions.create!(
          ip_address: request.remote_ip,
          user_agent: request.user_agent
        )

        cookies.signed.permanent[:session_id] = { value: session_record.id, httponly: true, same_site: :lax }

        render json: { message: "Logged in via Google successfully", user: { id: user.id, email: user.email_address, name: user.name, role: user.role } }, status: :ok
      end

      def failure
        render json: { error: "Authentication failed" }, status: :unauthorized
      end
    end
  end
end
