module Api
  module V1
    class SessionsController < ApplicationController
      allow_unauthenticated_access only: [:create]
      rate_limit to: 10, within: 3.minutes, only: :create

      def create
        if user = User.authenticate_by(params.permit(:email_address, :password))
          session_record = user.sessions.create!(
            ip_address: request.remote_ip,
            user_agent: request.user_agent
          )

          # Since it's an API, we could send a token (e.g. JWT) or rely on cookies.
          # We'll use the built-in Rails signed cookies if we rely on browser.
          # However, for REST APIs, returning the session ID or a token is common.
          # Here we align with standard Rails auth by setting the cookie.
          cookies.signed.permanent[:session_id] = { value: session_record.id, httponly: true, same_site: :lax }

          render json: { message: "Logged in successfully", user: { id: user.id, email: user.email_address, name: user.name, role: user.role } }, status: :ok
        else
          render json: { error: "Try another email address or password." }, status: :unauthorized
        end
      end

      def destroy
        terminate_session
        render json: { message: "Logged out successfully" }, status: :ok
      end
    end
  end
end
