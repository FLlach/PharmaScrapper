require 'swagger_helper'

RSpec.describe 'Api::V1::Sessions', type: :request do
  let(:user) { User.create!(email_address: 'test@example.com', password: 'password', password_confirmation: 'password', role: 'standard') }

  describe 'POST /api/v1/login' do
    context 'with valid credentials' do
      it 'creates a session and returns success' do
        expect {
          post '/api/v1/login', params: { email_address: user.email_address, password: 'password' }
        }.to change(Session, :count).by(1)

        expect(response).to have_http_status(:ok)

        json_response = JSON.parse(response.body)
        expect(json_response['message']).to eq('Logged in successfully')
        expect(json_response['user']['email']).to eq(user.email_address)

        # Check if the signed cookie is set
        expect(response.cookies['session_id']).to be_present
      end
    end

    context 'with invalid credentials' do
      it 'does not create a session and returns unauthorized' do
        expect {
          post '/api/v1/login', params: { email_address: user.email_address, password: 'wrongpassword' }
        }.not_to change(Session, :count)

        expect(response).to have_http_status(:unauthorized)

        json_response = JSON.parse(response.body)
        expect(json_response['error']).to eq('Try another email address or password.')
      end
    end
  end

  describe 'DELETE /api/v1/logout' do
    context 'when authenticated' do
      let!(:session_record) { user.sessions.create!(ip_address: '127.0.0.1', user_agent: 'RSpec') }

      before do
        # Since standard cookies array in RSpec request spec doesn't support signed cookies directly
        # we authenticate by logging in first to set the signed cookie properly.
        post '/api/v1/login', params: { email_address: user.email_address, password: 'password' }
      end

      it 'destroys the session and clears the cookie' do
        expect {
          delete '/api/v1/logout'
        }.to change(Session, :count).by(-1)

        expect(response).to have_http_status(:ok)
        json_response = JSON.parse(response.body)
        expect(json_response['message']).to eq('Logged out successfully')

        # Check that the cookie is cleared
        expect(response.cookies['session_id']).to be_blank
      end
    end

    context 'when not authenticated' do
      it 'returns unauthorized' do
        delete '/api/v1/logout'

        expect(response).to have_http_status(:unauthorized)
        json_response = JSON.parse(response.body)
        expect(json_response['error']).to eq('Unauthorized access')
      end
    end
  end
end
