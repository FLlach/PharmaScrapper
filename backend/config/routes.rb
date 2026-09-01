Rails.application.routes.draw do
  mount Rswag::Ui::Engine => '/api-docs'
  mount Rswag::Api::Engine => '/api-docs'
  namespace :api do
    namespace :v1 do
      match "auth/:provider/callback", to: "omniauth_callbacks#google_oauth2", via: [:get, :post]
      get "auth/failure", to: "omniauth_callbacks#failure"
      post "registrations", to: "registrations#create"
      post "login", to: "sessions#create"
      delete "logout", to: "sessions#destroy"

      resources :medicines, only: [:index] do
        member do
          get :comparison
        end
      end

      resources :pharmacies, only: [:index]
    end
  end

  get "up" => "rails/health#show", as: :rails_health_check
end
